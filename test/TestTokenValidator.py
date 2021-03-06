import unittest

from mlpkitsecurity.token_utils import (
    TokenCache,
    TokenManager,
    JWTTokenManager,
    TokenError,
    SecurityError,
    validate_scopes,
    retrieve_foundation_service_token,
    extract_zone_id,
    extract_scopes
)



public_key = '''
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxdRA7iHKUqDkDJM+paEq
luwgUn8MreHZSv/vJ3sdg21GPeXVtROOxLPyn6PBTRGp3UVmWTg+7YnyJrzwatbs
7IT3nti1bN/S/87yLneP/7dGebLreF3IgO2Nq6+foucIfa4wo2wDtjORtY2DgbCo
F7g8uhbjpI/Pt0aem1sU8qH3Tfvmx3C6Sa1uZY/M/lC+XgoQnqcjDTrRl+oYxBPy
h2GDjo1KTGZwCvC1stpbhZYp7dJLvM9bcRI11jpw1wzZ8Q0Uvd8gZ4JCGbYZDGIG
PGMzQ8YvLj509pjb3U8rKFEEfkzI1vK5HXBizgyLHlUEhwh/80w2xUab3+B3rJ1V
BQIDAQAB
-----END PUBLIC KEY-----'''

public_key_2 = '''
       -----BEGIN PUBLIC KEY-----
       MIGfMA0GCSqGSIb3DQEBAQUAA4
       GNADCBiQKBgQDdlatRjRjogo3W
       ojgGHFHYLugdUWAY9iR3fy4arW
       NA1KoS8kVw33cJibXr8bvwUAUp
       arCwlvdbH6dvEOfou0/gCFQsHU
       fQrSDv+MuSUMAe8jzKE4qW+jK+
       xQU9a03GUnKHkkle+Q0pX/g6jX
       Z7r1/xAK5Do2kQ+X5xK9cipRgE
       KwIDAQAB
       -----END PUBLIC KEY-----'''

token_expired_in_2085 = 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImxlZ2FjeS10b2tlbi1rZXkiLCJ0eXAiOiJKV1QifQ.eyJqdGkiOiI4Yzk3YWZjM2I4Mzk0N2E5OWVhMjMyNzE3Y2U3ZTFjMyIsInN1YiI6Im1scHRlc3RjbGllbnQiLCJhdXRob3JpdGllcyI6WyJtbHB0ZXN0Y2xpZW50Il0sInNjb3BlIjpbIm1scHRlc3RjbGllbnQiXSwiY2xpZW50X2lkIjoibWxwdGVzdGNsaWVudCIsImNpZCI6Im1scHRlc3RjbGllbnQiLCJhenAiOiJtbHB0ZXN0Y2xpZW50IiwiZ3JhbnRfdHlwZSI6ImNsaWVudF9jcmVkZW50aWFscyIsInJldl9zaWciOiJiNThjNWQ0ZiIsImlhdCI6MTQ4NjYzNDIzMSwiZXhwIjozNjMxMDgyMjMxLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvdWFhL29hdXRoL3Rva2VuIiwiemlkIjoidWFhIiwiYXVkIjpbIm1scHRlc3RjbGllbnQiXX0.nIl71Dxktizfb5B870Mlh_-62kN9_Wlda8WYbiz3iFaj22LzIUkQiRIAI57g3IwPXbJnJ1tlrf5_DIJpycRxzfxIZnW_GJW56sgY5L4mdPVHSIUHjeFh5v5tGwmOG6a1mYH_H0y8G-nHNolfSejcyvc4RYvcba4kS2nm-wDKKgfqDVaspM4Ktsa15eLHYn1P0LIUEsewTDm3qL_PgbJC3WKq_qgk02B5Or1n0doLkGBtccYlQEZ9lRixmkdov7_4Nl9UNTPgaYchC0AEaxd_RRCBK78FwC6tw3v1X3xJFXoYdJlMNOnTGdbQ4CVP5-Jd7gifPnUilPPPoJmITg0HZQ'

  #def validate(self, access_token, *, scopes=None, scope_regex=None, public_key=None, online=False):

class TestValidateTokenOffline(unittest.TestCase):
    def setUp(self):
        self.tm = JWTTokenManager(None)
    

    def test_validate_token_offline_success(self):
        token_ok, access_token = self.tm.validate(token_expired_in_2085, public_key=public_key)
        self.assertTrue(token_ok)
        self.assertEqual(access_token, token_expired_in_2085)

    def test_validate_token_offline_success_with_scopes(self):
        token_ok, access_token = self.tm.validate(token_expired_in_2085, public_key=public_key, scopes=['mlptestclient'])
        self.assertTrue(token_ok)
        self.assertEqual(access_token, token_expired_in_2085)

    def test_validate_token_offline_invalid_alg(self):
        token_with_alg_hs256 = 'Bearer eyJhbGciOiAiSFMyNTYiLCAia2lkIjogImxlZ2FjeS10b2tlbi1rZXkiLCAidHlwIjogIkpXVCJ9.eyJqdGkiOiI4Yzk3YWZjM2I4Mzk0N2E5OWVhMjMyNzE3Y2U3ZTFjMyIsInN1YiI6Im1scHRlc3RjbGllbnQiLCJhdXRob3JpdGllcyI6WyJtbHB0ZXN0Y2xpZW50Il0sInNjb3BlIjpbIm1scHRlc3RjbGllbnQiXSwiY2xpZW50X2lkIjoibWxwdGVzdGNsaWVudCIsImNpZCI6Im1scHRlc3RjbGllbnQiLCJhenAiOiJtbHB0ZXN0Y2xpZW50IiwiZ3JhbnRfdHlwZSI6ImNsaWVudF9jcmVkZW50aWFscyIsInJldl9zaWciOiJiNThjNWQ0ZiIsImlhdCI6MTQ4NjYzNDIzMSwiZXhwIjozNjMxMDgyMjMxLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvdWFhL29hdXRoL3Rva2VuIiwiemlkIjoidWFhIiwiYXVkIjpbIm1scHRlc3RjbGllbnQiXX0.nIl71Dxktizfb5B870Mlh_-62kN9_Wlda8WYbiz3iFaj22LzIUkQiRIAI57g3IwPXbJnJ1tlrf5_DIJpycRxzfxIZnW_GJW56sgY5L4mdPVHSIUHjeFh5v5tGwmOG6a1mYH_H0y8G-nHNolfSejcyvc4RYvcba4kS2nm-wDKKgfqDVaspM4Ktsa15eLHYn1P0LIUEsewTDm3qL_PgbJC3WKq_qgk02B5Or1n0doLkGBtccYlQEZ9lRixmkdov7_4Nl9UNTPgaYchC0AEaxd_RRCBK78FwC6tw3v1X3xJFXoYdJlMNOnTGdbQ4CVP5-Jd7gifPnUilPPPoJmITg0HZQ'
        self.assertRaises(SecurityError, self.tm.validate, token_with_alg_hs256,
                          public_key=public_key)


    def test_validate_token_offline_invalid_public_key(self):
        token =''
        self.assertRaises(SecurityError, self.tm.validate, token)

    def test_validate_token_offline_token_expired(self):
        token_expired = 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtleS1pZC0xIn0.eyJqdGkiOiIyYmZlYjYyOGVmNDk0MTFmYTk0ZTY1OTk4MjdiMjdiMCIsImV4dF9hdHRyIjp7ImVuaGFuY2VyIjoiWFNVQUEifSwic3ViIjoic2ItbWxmc2ctc3RkLTE4MDMhYjMxMyIsImF1dGhvcml0aWVzIjpbIm1sZnNnLXN0ZC0xODAzIWIzMTMucmV0cmFpbnNlcnZpY2UucmVhZCIsIm1sZnNnLXN0ZC0xODAzIWIzMTMuc3RvcmFnZWFwaS5hbGwiLCJtbGZzZy1zdGQtMTgwMyFiMzEzLm1vZGVscmVwby53cml0ZSIsIm1sZnNnLXN0ZC0xODAzIWIzMTMucmV0cmFpbnNlcnZpY2Uud3JpdGUiLCJ1YWEucmVzb3VyY2UiLCJtbGZzZy1zdGQtMTgwMyFiMzEzLmZ1bmN0aW9uYWxzZXJ2aWNlLmFsbCIsIm1sZnNnLXN0ZC0xODAzIWIzMTMubW9kZWxzZXJ2aWNlLnJlYWQiLCJtbGZzZy1zdGQtMTgwMyFiMzEzLm1vZGVsbWV0ZXJpbmcucmVhZCIsIm1sZnNnLXN0ZC0xODAzIWIzMTMubW9kZWxyZXBvLnJlYWQiLCJtbGZzZy1zdGQtMTgwMyFiMzEzLmRhdGFtYW5hZ2VtZW50LndyaXRlIiwibWxmc2ctc3RkLTE4MDMhYjMxMy5tb2RlbGRlcGxveW1lbnQuYWxsIiwibWxmc2ctc3RkLTE4MDMhYjMxMy5kYXRhbWFuYWdlbWVudC5yZWFkIl0sInNjb3BlIjpbIm1sZnNnLXN0ZC0xODAzIWIzMTMucmV0cmFpbnNlcnZpY2UucmVhZCIsIm1sZnNnLXN0ZC0xODAzIWIzMTMuc3RvcmFnZWFwaS5hbGwiLCJtbGZzZy1zdGQtMTgwMyFiMzEzLm1vZGVscmVwby53cml0ZSIsIm1sZnNnLXN0ZC0xODAzIWIzMTMucmV0cmFpbnNlcnZpY2Uud3JpdGUiLCJ1YWEucmVzb3VyY2UiLCJtbGZzZy1zdGQtMTgwMyFiMzEzLmZ1bmN0aW9uYWxzZXJ2aWNlLmFsbCIsIm1sZnNnLXN0ZC0xODAzIWIzMTMubW9kZWxzZXJ2aWNlLnJlYWQiLCJtbGZzZy1zdGQtMTgwMyFiMzEzLm1vZGVsbWV0ZXJpbmcucmVhZCIsIm1sZnNnLXN0ZC0xODAzIWIzMTMubW9kZWxyZXBvLnJlYWQiLCJtbGZzZy1zdGQtMTgwMyFiMzEzLmRhdGFtYW5hZ2VtZW50LndyaXRlIiwibWxmc2ctc3RkLTE4MDMhYjMxMy5tb2RlbGRlcGxveW1lbnQuYWxsIiwibWxmc2ctc3RkLTE4MDMhYjMxMy5kYXRhbWFuYWdlbWVudC5yZWFkIl0sImNsaWVudF9pZCI6InNiLW1sZnNnLXN0ZC0xODAzIWIzMTMiLCJjaWQiOiJzYi1tbGZzZy1zdGQtMTgwMyFiMzEzIiwiYXpwIjoic2ItbWxmc2ctc3RkLTE4MDMhYjMxMyIsImdyYW50X3R5cGUiOiJjbGllbnRfY3JlZGVudGlhbHMiLCJyZXZfc2lnIjoiNmM5MWI4ZjEiLCJpYXQiOjE1MjMyNjg0MjUsImV4cCI6MTUyMzMxMTYyNSwiaXNzIjoiaHR0cDovL2ZvdW5kYXRpb24ubG9jYWxob3N0OjgwODAvdWFhL29hdXRoL3Rva2VuIiwiemlkIjoiZm91bmRhdGlvbiIsImF1ZCI6WyJtbGZzZy1zdGQtMTgwMyFiMzEzLnN0b3JhZ2VhcGkiLCJtbGZzZy1zdGQtMTgwMyFiMzEzLm1vZGVscmVwbyIsIm1sZnNnLXN0ZC0xODAzIWIzMTMubW9kZWxkZXBsb3ltZW50IiwidWFhIiwibWxmc2ctc3RkLTE4MDMhYjMxMy5mdW5jdGlvbmFsc2VydmljZSIsIm1sZnNnLXN0ZC0xODAzIWIzMTMuZGF0YW1hbmFnZW1lbnQiLCJtbGZzZy1zdGQtMTgwMyFiMzEzLm1vZGVsbWV0ZXJpbmciLCJzYi1tbGZzZy1zdGQtMTgwMyFiMzEzIiwibWxmc2ctc3RkLTE4MDMhYjMxMy5tb2RlbHNlcnZpY2UiLCJtbGZzZy1zdGQtMTgwMyFiMzEzLnJldHJhaW5zZXJ2aWNlIl19.e6zz6EeRi_5rpevEUsQNiEpsgy1WKebFw6SIAUZ7TCBGOHaQUPWo4bXPlpgVgtUZJBqKKaGe0Fs9WgPJXwbt7DBV1f8i6OTi6osKEnyB0RPWYfSAqr6H3qKDuGYD08aIALX-kRzE_an0QD6QgkJbZ6BLxidXbxNmI0PBZiSmaID9NrrG2batOuGNOWfORn8ztnURPvHZpl7o5Te28jeiris1blEJhfBmiOmuUb-trevWEztlkBgSjai7bI90H85gFyrbYLCQCr13qnJwOW6PSI1Two2syzOb7S92ZVhfDY6CQNkW7lTgQ64zzh7RUJQiTTciaBpH-N-90iSNx3DTow'
        self.assertRaises(SecurityError, self.tm.validate, token_expired)

    def test_validate_token_offline_insufficient_scope(self):
        self.assertRaises(SecurityError, self.tm.validate, token_expired_in_2085, scopes=['some-required-scope', 'mlptestclient'],
                          public_key=public_key)


if __name__ == "__main__":
  unittest.main()