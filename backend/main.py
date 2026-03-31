from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import openpyxl
import shutil
import os

from database import init_db, get_db, User, Contract, ContractItem, Invoice
from auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, get_admin_user
)

app = FastAPI(title="HTZ 合同台账系统", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.on_event("startup")
def startup():
    init_db()
    # 创建默认管理员
    from database import SessionLocal
    db = SessionLocal()
    try:
        if not db.query(User).first():
            admin = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                is_admin=True
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


# ==================== 认证 ====================

from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False

@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token({"sub": user.username})
    return {"token": token, "username": user.username, "is_admin": user.is_admin}


@app.get("/api/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "is_admin": current_user.is_admin}


@app.post("/api/auth/users")
def create_user(req: UserCreate, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(username=req.username, hashed_password=get_password_hash(req.password), is_admin=req.is_admin)
    db.add(user)
    db.commit()
    return {"msg": "创建成功", "id": user.id}


@app.get("/api/auth/users")
def list_users(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "is_admin": u.is_admin} for u in users]


# ==================== 合同 ====================

class ContractCreate(BaseModel):
    seq: Optional[int] = None
    contract_no: str
    sign_date: Optional[str] = None
    amount: Optional[float] = None
    purchase_amount: Optional[float] = 0
    status: str = "进行中"
    buyer: Optional[str] = None
    content: Optional[str] = None
    invoice_info: Optional[str] = None
    order_progress: Optional[float] = 0
    delivery_progress: Optional[float] = 0


@app.get("/api/contracts")
def list_contracts(
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    buyer: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Contract)
    if keyword:
        query = query.filter(or_(
            Contract.contract_no.contains(keyword),
            Contract.content.contains(keyword),
            Contract.buyer.contains(keyword)
        ))
    if status:
        query = query.filter(Contract.status == status)
    if buyer:
        query = query.filter(Contract.buyer == buyer)
    
    total = query.count()
    items = query.order_by(Contract.id.desc()).offset((page - 1) * size).limit(size).all()
    
    return {
        "total": total,
        "items": [{
            "id": c.id, "seq": c.seq, "contract_no": c.contract_no,
            "sign_date": c.sign_date, "amount": c.amount, "purchase_amount": c.purchase_amount or 0,
            "status": c.status, "buyer": c.buyer, "content": c.content, "invoice_info": c.invoice_info,
            "order_progress": c.order_progress or 0, "delivery_progress": c.delivery_progress or 0
        } for c in items]
    }


@app.post("/api/contracts")
def create_contract(data: ContractCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if db.query(Contract).filter(Contract.contract_no == data.contract_no).first():
        raise HTTPException(status_code=400, detail="合同号已存在")
    contract = Contract(**data.model_dump())
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return {"msg": "创建成功", "id": contract.id}


@app.get("/api/contracts/{contract_id}")
def get_contract(contract_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")
    return {
        "id": contract.id, "seq": contract.seq, "contract_no": contract.contract_no,
        "sign_date": contract.sign_date, "amount": contract.amount, "purchase_amount": contract.purchase_amount or 0,
        "status": contract.status, "buyer": contract.buyer, "content": contract.content,
        "invoice_info": contract.invoice_info,
        "order_progress": contract.order_progress or 0, "delivery_progress": contract.delivery_progress or 0,
        "items": [{
            "id": i.id, "item_no": i.item_no, "material_code": i.material_code,
            "material_name": i.material_name, "unit": i.unit, "quantity": i.quantity,
            "contract_price": i.contract_price, "total_with_tax": i.total_with_tax,
            "purchase_price": i.purchase_price, "total_price": i.total_price,
            "purchase_contract_no": i.purchase_contract_no, "order_unit": i.order_unit,
            "sign_date": i.sign_date, "delivery_status": i.delivery_status,
            "delivery_date": i.delivery_date, "remark": i.remark
        } for i in contract.items]
    }


@app.put("/api/contracts/{contract_id}")
def update_contract(contract_id: int, data: ContractCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(contract, key, value)
    db.commit()
    return {"msg": "更新成功"}


@app.delete("/api/contracts/{contract_id}")
def delete_contract(contract_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")
    db.delete(contract)
    db.commit()
    return {"msg": "删除成功"}


# ==================== 合同明细 ====================

class ItemCreate(BaseModel):
    item_no: Optional[str] = None
    material_code: Optional[str] = None
    material_name: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[float] = 0
    contract_price: Optional[float] = 0
    total_with_tax: Optional[float] = 0
    purchase_price: Optional[float] = 0
    total_price: Optional[float] = 0
    purchase_contract_no: Optional[str] = None
    order_unit: Optional[str] = None
    sign_date: Optional[str] = None
    delivery_status: Optional[str] = None
    delivery_date: Optional[str] = None
    remark: Optional[str] = None


@app.post("/api/contracts/{contract_id}/items")
def create_item(contract_id: int, data: ItemCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")
    item = ContractItem(contract_id=contract_id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"msg": "添加成功", "id": item.id}


@app.put("/api/items/{item_id}")
def update_item(item_id: int, data: ItemCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(ContractItem).filter(ContractItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="明细不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    return {"msg": "更新成功"}


@app.delete("/api/items/{item_id}")
def delete_item(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(ContractItem).filter(ContractItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="明细不存在")
    db.delete(item)
    db.commit()
    return {"msg": "删除成功"}


@app.post("/api/contracts/{contract_id}/items/import")
async def import_items(contract_id: int, file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")
    
    filepath = os.path.join(UPLOAD_DIR, f"import_items_{contract_id}.xlsx")
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    wb = openpyxl.load_workbook(filepath)
    ws = wb.active
    
    count = 0
    errors = []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not row or not row[0]:
            continue
        try:
            def safe_float(v):
                if v is None: return 0
                try: return float(v)
                except: return 0
            
            def safe_str(v):
                return str(v).strip() if v is not None else None
            
            item = ContractItem(
                contract_id=contract_id,
                item_no=safe_str(row[0]),
                material_code=safe_str(row[1]),
                material_name=safe_str(row[2]),
                unit=safe_str(row[3]),
                quantity=safe_float(row[4]),
                contract_price=safe_float(row[5]),
                total_with_tax=safe_float(row[6]),
                purchase_price=safe_float(row[7]),
                total_price=safe_float(row[8]),
                purchase_contract_no=safe_str(row[9]) if len(row) > 9 else None,
                order_unit=safe_str(row[10]) if len(row) > 10 else None,
                sign_date=safe_str(row[11]) if len(row) > 11 else None,
                delivery_status=safe_str(row[12]) if len(row) > 12 else None,
                delivery_date=safe_str(row[13]) if len(row) > 13 else None,
                remark=safe_str(row[14]) if len(row) > 14 else None,
            )
            db.add(item)
            count += 1
        except Exception as e:
            errors.append(f"第{row_idx}行: {str(e)}")
    
    db.commit()
    return {"msg": f"导入完成", "imported": count, "errors": errors}


@app.get("/api/contracts/{contract_id}/items/export")
def export_items(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")
    
    items = db.query(ContractItem).filter(ContractItem.contract_id == contract_id).all()
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "合同明细"
    
    headers = ["项目号", "物料编码", "物料名称", "单位", "数量", "合同单价", "总计（含税）", "采购价", "总价", "采购合同号", "订货单位", "签订日期", "交货情况", "交货期", "备注"]
    ws.append(headers)
    
    for i in items:
        ws.append([i.item_no, i.material_code, i.material_name, i.unit, i.quantity, i.contract_price, i.total_with_tax, i.purchase_price, i.total_price, i.purchase_contract_no, i.order_unit, i.sign_date, i.delivery_status, i.delivery_date, i.remark])
    
    # 汇总行
    from sqlalchemy import func
    total_sales = db.query(func.sum(ContractItem.total_with_tax)).filter(ContractItem.contract_id == contract_id).scalar() or 0
    total_purchase = db.query(func.sum(ContractItem.total_price)).filter(ContractItem.contract_id == contract_id).scalar() or 0
    ws.append([])
    ws.append(["", "", "", "", "", "", "销售金额合计:", "", total_sales])
    ws.append(["", "", "", "", "", "", "采购金额合计:", "", total_purchase])
    
    filepath = os.path.join(UPLOAD_DIR, f"export_items_{contract_id}.xlsx")
    wb.save(filepath)
    
    from fastapi.responses import FileResponse
    return FileResponse(filepath, filename=f"{contract.contract_no}_明细.xlsx")


@app.get("/api/template/items")
def download_item_template():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "合同明细模板"
    
    headers = ["项目号", "物料编码", "物料名称", "单位", "数量", "合同单价", "总计（含税）", "采购价", "总价", "采购合同号", "订货单位", "签订日期", "交货情况", "交货期", "备注"]
    ws.append(headers)
    ws.append(["1", "MAT001", "示例物料名称", "台", 2, 5000, 10000, 4500, 9000, "PO2025001", "示例公司", "2025.1.1", "未交货", "30天", ""])
    for i in range(1, len(headers)+1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = 15
    
    filepath = os.path.join(UPLOAD_DIR, "template_items.xlsx")
    wb.save(filepath)
    from fastapi.responses import FileResponse
    return FileResponse(filepath, filename="合同明细导入模板.xlsx")


@app.get("/api/template/contracts")
def download_contract_template():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "合同导入模板"
    
    headers = ["序号", "供应合同号", "签订日期", "合同金额", "采购金额", "合同状态", "采购员", "合同内容", "开票信息"]
    ws.append(headers)
    ws.append([1, "2501CBHW0001", "2025.1.1", 10000, 8000, "进行中", "文旭", "示例合同内容", ""])
    for i in range(1, len(headers)+1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = 20
    
    filepath = os.path.join(UPLOAD_DIR, "template_contracts.xlsx")
    wb.save(filepath)
    from fastapi.responses import FileResponse
    return FileResponse(filepath, filename="合同导入模板.xlsx")


# ==================== 发票 ====================

class InvoiceCreate(BaseModel):
    invoice_no: str
    invoice_date: Optional[str] = None
    amount: Optional[float] = None
    tax_amount: Optional[float] = None
    contract_id: Optional[int] = None
    seller: Optional[str] = None
    attachment_path: Optional[str] = None
    attachment_name: Optional[str] = None


@app.get("/api/invoices")
def list_invoices(
    keyword: Optional[str] = None,
    contract_id: Optional[int] = None,
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Invoice)
    if keyword:
        query = query.filter(or_(
            Invoice.invoice_no.contains(keyword),
            Invoice.seller.contains(keyword)
        ))
    if contract_id:
        query = query.filter(Invoice.contract_id == contract_id)
    
    total = query.count()
    items = query.order_by(Invoice.id.desc()).offset((page - 1) * size).limit(size).all()
    
    return {
        "total": total,
        "items": [{
            "id": i.id, "invoice_no": i.invoice_no, "invoice_date": i.invoice_date,
            "amount": i.amount, "tax_amount": i.tax_amount,
            "contract_id": i.contract_id, "seller": i.seller, "file_path": i.file_path,
            "attachment_path": i.attachment_path, "attachment_name": i.attachment_name
        } for i in items]
    }


@app.post("/api/invoices")
def create_invoice(data: InvoiceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if db.query(Invoice).filter(Invoice.invoice_no == data.invoice_no).first():
        raise HTTPException(status_code=400, detail="发票号已存在")
    invoice = Invoice(**data.model_dump())
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return {"msg": "创建成功", "id": invoice.id}


@app.put("/api/invoices/{invoice_id}")
def update_invoice(invoice_id: int, data: InvoiceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="发票不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(invoice, key, value)
    db.commit()
    return {"msg": "更新成功"}


@app.delete("/api/invoices/{invoice_id}")
def delete_invoice(invoice_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="发票不存在")
    db.delete(invoice)
    db.commit()
    return {"msg": "删除成功"}


@app.post("/api/invoices/upload")
async def upload_invoice_pdf(
    file: UploadFile = File(...),
    invoice_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 创建发票附件专用目录
    attach_dir = os.path.join(UPLOAD_DIR, "invoice_attachments")
    os.makedirs(attach_dir, exist_ok=True)
    
    # 用发票号或时间戳命名，避免冲突
    original_name = file.filename or "attachment.pdf"
    if invoice_id:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice:
            safe_name = f"{invoice.invoice_no}_{original_name}"
            # 更新发票记录的附件信息
            filepath = os.path.join(attach_dir, safe_name)
            with open(filepath, "wb") as f:
                shutil.copyfileobj(file.file, f)
            invoice.attachment_path = f"/uploads/invoice_attachments/{safe_name}"
            invoice.attachment_name = original_name
            db.commit()
            return {"msg": "上传成功", "path": invoice.attachment_path, "name": original_name}
    
    # 无invoice_id时，用时间戳命名
    import time
    safe_name = f"{int(time.time())}_{original_name}"
    filepath = os.path.join(attach_dir, safe_name)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"msg": "上传成功", "path": f"/uploads/invoice_attachments/{safe_name}", "name": original_name}


# ==================== 导入导出 ====================

@app.post("/api/import/contracts")
async def import_contracts(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    filepath = os.path.join(UPLOAD_DIR, "import_contracts.xlsx")
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    wb = openpyxl.load_workbook(filepath)
    ws = wb.active
    
    count = 0
    errors = []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not row or not row[0]:
            continue
        try:
            # 兼容老格式(8列)和新格式(9列)
            if len(row) <= 8:
                seq, contract_no, sign_date, amount, status_val, buyer, content, invoice_info = (
                    row[0], row[1], str(row[2]) if row[2] else None,
                    float(row[3]) if row[3] else None,
                    row[4] if row[4] and row[4] in ['进行中','待开票','待回款','已完结','已开票','已交货','未交货'] else "进行中",
                    row[5], row[6],
                    row[7] if len(row) > 7 else None
                )
                purchase_amount = 0
            else:
                seq, contract_no, sign_date, amount, purchase_amount, status_val, buyer, content, invoice_info = (
                    row[0], row[1], str(row[2]) if row[2] else None,
                    float(row[3]) if row[3] else None,
                    float(row[4]) if row[4] else 0,
                    row[5] if row[5] and row[5] in ['进行中','待开票','待回款','已完结','已开票','已交货','未交货'] else "进行中",
                    row[6] if len(row) > 6 else None,
                    row[7] if len(row) > 7 else None,
                    row[8] if len(row) > 8 else None
                )
            
            # 映射老状态到新状态
            status_map = {'已开票': '待回款', '已交货': '待开票', '未交货': '进行中'}
            status_val = status_map.get(status_val, status_val) if status_val else "进行中"
            
            existing = db.query(Contract).filter(Contract.contract_no == str(contract_no)).first()
            if existing:
                existing.seq = seq
                existing.sign_date = sign_date
                existing.amount = amount
                existing.purchase_amount = purchase_amount
                existing.status = status_val
                existing.buyer = buyer
                existing.content = content
                existing.invoice_info = invoice_info
            else:
                contract = Contract(
                    seq=seq, contract_no=str(contract_no), sign_date=sign_date,
                    amount=amount, purchase_amount=purchase_amount, status=status_val, buyer=buyer,
                    content=content, invoice_info=invoice_info
                )
                db.add(contract)
            count += 1
        except Exception as e:
            errors.append(f"第{row_idx}行: {str(e)}")
    
    db.commit()
    return {"msg": f"导入完成", "imported": count, "errors": errors}


@app.get("/api/export/contracts")
def export_contracts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contracts = db.query(Contract).order_by(Contract.seq).all()
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "合同台账"
    
    headers = ["序号", "供应合同号", "签订日期", "合同金额", "采购金额", "合同状态", "采购员", "合同内容", "开票信息", "订货进度%", "交货进度%"]
    ws.append(headers)
    
    for c in contracts:
        ws.append([c.seq, c.contract_no, c.sign_date, c.amount, c.purchase_amount or 0, c.status, c.buyer, c.content, c.invoice_info, c.order_progress or 0, c.delivery_progress or 0])
    
    filepath = os.path.join(UPLOAD_DIR, "export_contracts.xlsx")
    wb.save(filepath)
    
    from fastapi.responses import FileResponse
    return FileResponse(filepath, filename="合同台账.xlsx")


@app.get("/api/export/invoices")
def export_invoices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    invoices = db.query(Invoice).all()
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "发票台账"
    
    headers = ["发票号码", "开票日期", "价税合计", "税额", "关联合同号", "销售方"]
    ws.append(headers)
    
    for i in invoices:
        contract_no = i.contract.contract_no if i.contract else ""
        ws.append([i.invoice_no, i.invoice_date, i.amount, i.tax_amount, contract_no, i.seller])
    
    filepath = os.path.join(UPLOAD_DIR, "export_invoices.xlsx")
    wb.save(filepath)
    
    from fastapi.responses import FileResponse
    return FileResponse(filepath, filename="发票台账.xlsx")


# ==================== 统计 ====================

@app.get("/api/stats")
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total_contracts = db.query(Contract).count()
    total_invoices = db.query(Invoice).count()
    
    from sqlalchemy import func
    total_amount = db.query(func.sum(Contract.amount)).scalar() or 0
    total_invoice_amount = db.query(func.sum(Invoice.amount)).scalar() or 0
    
    # 明细汇总
    total_sales = db.query(func.sum(ContractItem.total_with_tax)).scalar() or 0
    total_purchase = db.query(func.sum(ContractItem.total_price)).scalar() or 0
    total_items = db.query(ContractItem).count()
    
    by_status = {}
    for status_val in ["已开票", "已交货", "未交货"]:
        by_status[status_val] = db.query(Contract).filter(Contract.status == status_val).count()
    
    by_buyer = {}
    buyers = db.query(Contract.buyer, func.count(Contract.id), func.sum(Contract.amount)).group_by(Contract.buyer).all()
    for buyer, count, amount in buyers:
        by_buyer[buyer or "未知"] = {"count": count, "amount": amount or 0}
    
    return {
        "total_contracts": total_contracts,
        "total_invoices": total_invoices,
        "total_amount": total_amount,
        "total_invoice_amount": total_invoice_amount,
        "total_sales": total_sales,
        "total_purchase": total_purchase,
        "total_items": total_items,
        "by_status": by_status,
        "by_buyer": by_buyer
    }
