import pytest
from shared.tenant.context import _tenant_id_ctx

@pytest.fixture(autouse=True)
def set_tenant():
    token = _tenant_id_ctx.set("test-tenant-auftragsai")
    yield
    _tenant_id_ctx.reset(token)
