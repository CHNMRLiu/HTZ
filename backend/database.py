from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./data/htz.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)


class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    seq = Column(Integer, comment="序号")
    contract_no = Column(String(50), unique=True, index=True, comment="供应合同号")
    sign_date = Column(String(20), comment="签订日期")
    amount = Column(Float, comment="合同金额/销售金额")
    purchase_amount = Column(Float, default=0, comment="采购金额")
    status = Column(String(20), default="进行中", comment="合同状态: 进行中/待开票/待回款/已完结")
    buyer = Column(String(20), comment="采购员")
    content = Column(Text, comment="合同内容")
    invoice_info = Column(Text, comment="开票日期-开票号码（金额）")
    order_progress = Column(Float, default=0, comment="订货进度百分比")
    delivery_progress = Column(Float, default=0, comment="交货进度百分比")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    invoices = relationship("Invoice", back_populates="contract")
    items = relationship("ContractItem", back_populates="contract", cascade="all, delete-orphan")


class ContractItem(Base):
    __tablename__ = "contract_items"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, comment="关联合同")
    item_no = Column(String(20), comment="项目号/序号")
    material_code = Column(String(50), comment="物料编码")
    material_name = Column(String(200), comment="物料名称")
    unit = Column(String(20), comment="单位")
    quantity = Column(Float, default=0, comment="数量")
    contract_price = Column(Float, default=0, comment="合同单价")
    total_with_tax = Column(Float, default=0, comment="总计（含税）")
    purchase_price = Column(Float, default=0, comment="采购价")
    total_price = Column(Float, default=0, comment="总价")
    purchase_contract_no = Column(String(50), comment="采购合同号")
    order_unit = Column(String(100), comment="订货单位")
    sign_date = Column(String(20), comment="签订日期")
    delivery_status = Column(String(50), comment="交货情况")
    delivery_date = Column(String(50), comment="交货期")
    remark = Column(Text, comment="备注")
    
    contract = relationship("Contract", back_populates="items")


class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String(50), unique=True, index=True, comment="发票号码")
    invoice_date = Column(String(20), comment="开票日期")
    amount = Column(Float, comment="价税合计")
    tax_amount = Column(Float, comment="税额")
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True, comment="关联合同")
    seller = Column(String(100), comment="销售方")
    file_path = Column(String(255), comment="PDF文件路径")
    created_at = Column(DateTime, default=datetime.now)
    
    contract = relationship("Contract", back_populates="invoices")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
