import pytest
from unittest.mock import Mock

import Crypto
from bibifi.authfile import Keys

def multi_side_effect(*args):
    effects = iter(args)

    def effect(*args):
        cur = next(effects)
        if isinstance(cur, Exception):
            raise cur
        elif callable(cur):
            return cur(*args)
        else:
            return cur

    return effect

def fill_buffer(values):
    def filler(buf):
        size = min(len(buf), len(values))
        buf[:size] = values[:size]
        return size
    return filler

def generate_data(length):
    return bytes(x * 3773 % 256 for x in range(0, length))

@pytest.fixture(scope='session')
def rsa_key():
    return Crypto.PublicKey.RSA.importKey(rsa_keys_encoded[0])

@pytest.fixture(scope='session')
def bad_rsa_key():
    return Crypto.PublicKey.RSA.importKey(rsa_keys_encoded[1])

@pytest.fixture(scope='session')
def keys(rsa_key, bad_rsa_key):
    return Keys(rsa_key, bad_rsa_key)

@pytest.fixture
def sha512():
    return Crypto.Hash.SHA512.new()
    
@pytest.fixture(scope='session')
def bad_signer(bad_rsa_key):
    return Crypto.Signature.PKCS1_PSS.new(bad_rsa_key)    

@pytest.fixture(scope='session')
def signer(rsa_key):
    return Crypto.Signature.PKCS1_PSS.new(rsa_key)

rsa_keys_encoded = [
    b'-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAoJzjO2Nar2XAu4P6hJdhbmI+BhAwGqdOsRG+jvwR6eUl4PRU\nMFW/fMSNdcA01+bsZF6PckzjY3P6E75PPujOPGw/vQZJ3QOuIqe/yYdduHZXjOaH\nR4RHkqnDNPsHtFBhC0k8xbSBvNXZD+FCF13NbV56FW0zluonZkPYyNWG0v1I5uf7\n6gxnlTiAZe0s7NIyyL0EwE60ya7z38VEOGA/qL1Vth5KmjvV3PsBwUV4haUdnIyo\ncfyryqKBZgnQpFMow1dJAiQnvlK++PyUHQOj5TIdq3QCCtULX/IGJKMSMP+k1iCU\ng0eadOAAQUGhXzI1Zx4wLYL9QRMcDU0vO+obHQIDAQABAoIBAAaUhua++k8nTw8f\nqBrYjOBV3A6piR7+bcXpYTJAd4dqoPOnbu+QA8lb0CPb3Q5fYp32FdBsAADqFnvK\nlzqPlSt6j93xrQMGDJNU5hGenyNYjduy8iXm8Hu8wsef5T/o7yDkPj4nWA1hgYQa\nCXglmq35ae0IzU1IiJay/uWzgdORBkUkmjiFZJ1yTblqFbCjDIGBiSay+ubUkvo8\nI419SowUn6z2BlLMIuZgx65KaidMHPBYVo/YVuQYYDzl7Hw9PR/e2Lg+sJrAhH30\n+d3zptysvbFR9BsVC/Bq8wNmO0dX+NTUfWi8CsulXJq6oia8YzIEbWd9p9mZ/7SH\nwWwKeY0CgYEAuPizJ1cyIUmJjbcMLcWt2pUX+uKv3cWqejUzcEF8GT9lJG44VLIW\n51hLwS3FSRaD7PbRaVgt7ueuF46wEbc4GnAWPncwo2CGLeaTA5RxBmsbQK8sqAgE\ngjSfcuS1om67tsZsquciwSKwM0HBcQFbFSNHxViMLITPF0bCK/Tjce8CgYEA3kmn\nZlf3b+GSnUgFN7f+w+NcUsgnyuzNq6UfuIpnb5nDYgqeznN+fTMyDy5Uwt06JdRs\ngDQhzt1+oZd0T3Py+gGkVXmPOp961UsZA+g/x01Qs8pygIbaKeAzpHlNMXGs4zYA\nKlPUbEbTY1kBrZ0xbICDPJj8mVDTrG+j5vrCn7MCgYBK28PNiRltpVA4/Tq9j4IT\ns0E4NOPN0gBzYvKFXMs3gJOTUdQUWtqwF+jYrohoUudjUGRhyOEWDcdEG2ggU1Eu\nSeyGrUAO7rJ/AxC+YyX23gPygrKE8nG4rElXez4TFdN8XgN+ivpixYIfzF3YOR8+\nh7+1G2fnYHxbRDSzC3G9GwKBgC38YstDa4cTzXcITTwHrobr5E+j5MeQUcQutu9A\ngsGNt+PyeoQPVJ2mF7cYSKS/i6YD2iZzooLfQ7E+WeuN+zhJWqvsJ/tivtCdZqFu\nTLN4hTeMrD92pm9/WG+wQI34DGI866/WA94akOS+pyA5ot3lgEDrDWbSV9gWiHvi\naJ0NAoGBAJ4JLWtz3cSqFqlxuhmLbcD4VZWiHIUCwg34id2WRk9TT2aT3hfL90U0\nYZt/ExXJ9OVfS01OxdF9w1Q7+wba8leZ4DMth0/kccN0mVsQN208wPBD7BK/eLwm\nerEECiUtyocV1Tr0qoadmEdFFDZu8m8yaOqpgWG7Mpu89KP6q+oL\n-----END RSA PRIVATE KEY-----',
    b'-----BEGIN RSA PRIVATE KEY-----\nMIIEpQIBAAKCAQEA7UPs8UdVk+jFZG/2SaOreft+oZcXb3aEiCDQAGnj6QC+5vVS\nYTCWgcNBnS82/hu/XwBfSdhgVQdOau/82IBrCPPD41qBKxa8cqPgaz9JxW9iKmPB\nhdGALWgzn5zl0sH3dZUkgD4euMFsIEtF06lkHyAopDxRQ7VoayrTBShllrgRdzJ1\n45qs4SfKghB3l8a14UljkUU+gVc74MN2kp+fCElgngxi699LUCQAyQQ2CCfpeHxk\nUmGTBCtXJUA1MAsr/87cHfNogkjgPJTQBuwBzySYKmWzF4J8azA0Ikyb9QQuBHFL\nJRktzeWwLo1PRmKy0lCuvrkD1qXRGuLsKbuaYQIDAQABAoIBAQC6wwQIrHEFe22d\ncLA6KPY6j6ePBMKyv2T1TnbMTI3VA/xBCows6rUeMZc9ZkPwY+EQo9dd5k91vsmQ\nTZYGyZb3NgJUvRH92+i8iJiHcwrbuaBY46sabd1qYKJ6GmOhsYLbcGmJ9Nvz7HTz\nOq0dPjIMeiDjnoMNPAeUi+INJk5JAtihEV+OXyEn7T6nj97ChbgIUtwh6Gs+SXo5\noP9lXoBayfC3cqbFT5C12AXS8UOkFf0pKPxppvmSl9yWG4nyJtaeQf/X/rUWPe9F\na9Bq6gs84RyzWnmiPCezPId4KCrw+B7Ciz4332b2isikxq4z5TBB0NZUejv8cAUE\nS5P8M3U9AoGBAO127Oh73odnrr5nBC1FoNVVkbiCqGXCPQ+qvziNIuXH1HGgF3Rl\ncSpHW8y4+M1X3y0C+3KKK7n4vxgjsEl/PFV9Yz5TlmkiLPMQy6CFcAyoRnUjJBzk\nZyxdLeTPQ6n9DicVkvZnM4/2MaHIFYd3f9QJvHv+H2m/+V/QL2bWHXZbAoGBAP/J\nBPFObsnYx8tOcSGpSC4Zb9GpVJobP0UNfeSEIWZ52z9oQaaYELH2OUFpdVILA+Km\nS06Y6ndrcJ3/jUAmGPV1xJaepV16uQqTtb5K+pg8CnqQemW6Ozya0tH+Rb7BSLVf\nCmTnb1OVi2/1xej5fgHCVesT2RMntbXROLPmlGbzAoGAMMu+VOuXR6XDn7aVgiQL\nr6rcvdiDeB2Y5I5Gqv09jZAplIu8JhvuTCzLrV7ZKYEECEDToK7J23ZE9lXnFMND\nh6GzcgxFHSd7qxrpbPvekYtGpy1ob1Nz7AbdtmXs1pJ8hQWG5IFCdDO38TGnUuX4\na37wr14B4H4lZU3nX69h8H8CgYEA7kvYzvbDQEk12bK6syGCnXAVPL8Eko3P5AUt\nxDdU5qOgHvKCNzJ0W1eI/+e/5S9d70n93ruXtKnjwU7TyW+00PlmrOwgI3ax7aiv\nKRmxXSKSoJz5asyVY2DaB8lcMNrhYhepF1iF3tjzjtrqBqJpQjpK0TcshSv5nenN\naczndQECgYEApvTWT9hiEeZpVmxgWlxdqxsWwxYXJXoAT3FcW4wMjPXeJ1eCtezz\nFenivNKed6teg4WTuhDkQiib9an9ozlfkcyZU06BVyxYfuLTAv6zbXyDS7wFNaRC\nGId6Bnn+gtyfAmy7VrOHk596XZvbGSneOsige6nKmgwtBKkfnsRrRN0=\n-----END RSA PRIVATE KEY-----',
]
