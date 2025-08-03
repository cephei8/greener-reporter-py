import contextlib
import json
import os

import pytest
from pydantic import UUID4

from greener_reporter import Reporter, Error as ReporterError, TestcaseStatus
from greener_servermock import Servermock
from greener_servermock.iotypes import (
    Calls,
    CallFunc,
    CallReportStatus,
    Responses,
    ResponseStatus,
)


def fixture_names():
    sm = Servermock()
    names = sm.fixture_names()
    return names


@pytest.fixture(params=fixture_names())
def fixture_name(request):
    return request.param


@pytest.fixture
def servermock_context():
    sm = Servermock()
    yield sm
    sm.shutdown()


@pytest.fixture
def servermock_calls(fixture_name, servermock_context):
    return servermock_context.fixture_calls(fixture_name)


@pytest.fixture
def servermock_responses(fixture_name, servermock_context):
    return servermock_context.fixture_responses(fixture_name)


@pytest.fixture
def servermock_serve(fixture_name, servermock_context, servermock_responses):
    servermock_context.serve(servermock_responses)
    addr = f"http://localhost:{servermock_context.port}"
    yield addr


@pytest.fixture
def reporter(servermock_serve):
    reporter = Reporter(servermock_serve, "some-api-key")
    yield reporter


def test_integration(reporter, servermock_context, servermock_calls, servermock_responses):
    calls = Calls(**servermock_calls)
    responses = Responses(**servermock_responses)

    def call_create_session():
        def f():
            return reporter.create_session(
                str(call.payload.id) if call.payload.id else None,
                call.payload.description,
                json.dumps(call.payload.baggage) if call.payload.baggage else None,
                call.payload.labels,
            )

        def success_handler():
            session = f()
            assert UUID4(session.id) == responses.create_session_response.payload.id

        def error_handler():
            with pytest.raises(ReporterError):
                f()

        h = {
            ResponseStatus.SUCCESS: success_handler,
            ResponseStatus.ERROR: error_handler,
        }
        h[responses.create_session_response.status]()

    def call_create_testcase():
        def f():
            for p in call.payload.testcases:
                reporter.create_testcase(
                    p.session_id,
                    p.testcase_name,
                    p.testcase_classname,
                    p.testcase_file,
                    p.testsuite,
                    {
                        CallReportStatus.PASS: TestcaseStatus.PASS,
                        CallReportStatus.FAIL: TestcaseStatus.FAIL,
                        CallReportStatus.ERR: TestcaseStatus.ERR,
                        CallReportStatus.SKIP: TestcaseStatus.SKIP,
                    }[p.status],
                    None,
                    None,
                )

        def success_handler():
            f()

        def error_handler():
            with pytest.raises(ReporterError):
                f()

        h = {
            ResponseStatus.SUCCESS: success_handler,
            ResponseStatus.ERROR: error_handler,
        }
        h[responses.report_response.status]()

    call_handlers = {
        CallFunc.CREATE_SESSION: call_create_session,
        CallFunc.REPORT: call_create_testcase,
    }

    for call in calls.calls:
        call_handlers[call.func]()

    reporter.shutdown()

    servermock_context.assert_calls(servermock_calls)
