from ctypes import (
    POINTER,
    byref,
    c_int,
    cdll,
    Structure,
    c_char_p,
)
from typing import Optional
from enum import Enum
import json
import pathlib
import platform

_PREFIX = {"Darwin": "lib", "Linux": "lib", "Windows": ""}[platform.system()]
_EXT = {"Darwin": ".dylib", "Linux": ".so", "Windows": ".dll"}[platform.system()]
_LIB_NAME = f"{_PREFIX}greener_reporter{_EXT}"
_LIB_PATH = pathlib.Path(__file__).parent.resolve() / _LIB_NAME


class _Reporter(Structure):
    pass


class _Session(Structure):
    _fields_ = [("id", c_char_p)]


class _Error(Structure):
    _fields_ = [("code", c_int), ("ingress_code", c_int), ("message", c_char_p)]


class Error(Exception):
    def __init__(self, code: int, ingress_code: int, message: str):
        self.code = code
        self.ingress_code = ingress_code
        self.message = message


class Session(Exception):
    def __init__(self, session_id: str):
        self.id = session_id


class TestcaseStatus(str, Enum):
    __test__ = False

    PASS = "pass"
    FAIL = "fail"
    ERR = "error"
    SKIP = "skip"


class Reporter:
    def __init__(self, endpoint: str, api_key: str):
        self._lib = cdll.LoadLibrary(str(_LIB_PATH))

        self._lib.greener_reporter_new.restype = POINTER(_Reporter)
        self._lib.greener_reporter_new.argtypes = [
            c_char_p,
            c_char_p,
            POINTER(POINTER(_Error)),
        ]

        self._lib.greener_reporter_delete.restype = None
        self._lib.greener_reporter_delete.argtypes = [
            POINTER(_Reporter),
            POINTER(POINTER(_Error)),
        ]

        self._lib.greener_reporter_session_create.restype = POINTER(_Session)
        self._lib.greener_reporter_session_create.argtypes = [
            POINTER(_Reporter),
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
            POINTER(POINTER(_Error)),
        ]

        self._lib.greener_reporter_testcase_create.restype = None
        self._lib.greener_reporter_testcase_create.argtypes = [
            POINTER(_Reporter),
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
            POINTER(POINTER(_Error)),
        ]

        self._lib.greener_reporter_report_error_pop.restype = None
        self._lib.greener_reporter_report_error_pop.argtypes = [
            POINTER(_Reporter),
            POINTER(POINTER(_Error)),
        ]

        self._lib.greener_reporter_session_delete.restype = None
        self._lib.greener_reporter_session_delete.argtypes = [
            POINTER(_Session),
        ]

        self._lib.greener_reporter_error_delete.restype = None
        self._lib.greener_reporter_error_delete.argtypes = [
            POINTER(_Error),
        ]

        # ----------------------------------------------------------------------

        err = POINTER(_Error)()
        self._handle = self._lib.greener_reporter_new(
            c_char_p(endpoint.encode()),
            c_char_p(api_key.encode()),
            byref(err),
        )
        self._verify_call(err)

    def _verify_call(self, err) -> None:
        if err:
            e = Error(
                err.contents.code,
                err.contents.ingress_code,
                err.contents.message.decode(),
            )
            self._lib.greener_reporter_error_delete(err)
            raise e

    def shutdown(self):
        err = POINTER(_Error)()
        self._lib.greener_reporter_delete(
            self._handle,
            byref(err),
        )
        try:
            self._verify_call(err)
        finally:
            self._handle = None

    def create_session(
            self,
            session_id: Optional[str],
            description: Optional[str],
            baggage: Optional[str],
            labels: Optional[str],
    ) -> Session:
        err = POINTER(_Error)()
        session_p = self._lib.greener_reporter_session_create(
            self._handle,
            (
                c_char_p(session_id.encode())
                if session_id is not None
                else c_char_p()
            ),
            (
                c_char_p(description.encode())
                if description is not None
                else c_char_p()
            ),
            (
                c_char_p(baggage.encode())
                if baggage is not None
                else c_char_p()
            ),
            (
                c_char_p(labels.encode())
                if labels is not None
                else c_char_p()
            ),
            byref(err),
        )
        self._verify_call(err)

        session = Session(session_p.contents.id.decode())
        self._lib.greener_reporter_session_delete(session_p)

        return session

    def create_testcase(
        self,
        session_id: str,
        testcase_name: str,
        testcase_classname: Optional[str],
        testcase_file: Optional[str],
        testsuite: Optional[str],
        status: TestcaseStatus,
        output: Optional[str],
        baggage: Optional[dict],
    ):
        err = POINTER(_Error)()
        self._lib.greener_reporter_testcase_create(
            self._handle,
            c_char_p(session_id.encode()),
            c_char_p(testcase_name.encode()),
            (
                c_char_p(testcase_classname.encode())
                if testcase_classname is not None
                else c_char_p()
            ),
            (
                c_char_p(testcase_file.encode())
                if testcase_file is not None
                else c_char_p()
            ),
            c_char_p(testsuite.encode()) if testsuite is not None else c_char_p(),
            c_char_p(status.value.encode()),
            c_char_p(output.encode()) if output is not None else c_char_p(),
            (
                c_char_p(json.dumps(baggage).encode())
                if baggage is not None
                else c_char_p()
            ),
            byref(err),
        )
        self._verify_call(err)

    def pop_error(self):
        err = POINTER(_Error)()
        self._lib.greener_reporter_report_error_pop(self._handle, byref(err))
        self._verify_call(err)
