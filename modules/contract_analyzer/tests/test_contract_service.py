from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared.db.session import Base
from shared.tenant.context import _tenant_id_ctx
from modules.contract_analyzer.src.contracts.services.contract_service import ContractService
from modules.contract_analyzer.src.contracts.db_models import Contract


class TestContractService:
    def setup_method(self):
        # In-Memory-DB für Unit-Test
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        self.Session = sessionmaker(bind=engine)
        _tenant_id_ctx.set("test-tenant-contracts")
        self.service = ContractService()

    def test_register_contract_persists_row(self):
        session = self.Session()
        contract = self.service.register_contract(
            session=session,
            file_name="vertrag_xyz.pdf",
            mime_type="application/pdf",
            counterparty_name="Firma XYZ",
            payment_terms_days=30,
            uploaded_by="jurist",
        )
        session.commit()

        db_contract = session.query(Contract).filter_by(document_id=contract.document_id).first()
        assert db_contract is not None
        assert db_contract.tenant_id == "test-tenant-contracts"
        assert db_contract.counterparty_name == "Firma XYZ"
        assert db_contract.payment_terms_days == 30
