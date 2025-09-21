# OdooXNmit
pvt project
https://drive.google.com/drive/folders/1kkBEBrqfbFkQrTRJHJurGaL9hP1JIFYU?usp=sharing
vdo file


# 📘 CraftERP – Manufacturing ERP System

CraftERP is a lightweight **Manufacturing ERP (Enterprise Resource Planning) system** built with **Flask (Python)** for the backend, **MongoDB/PostgreSQL** for data storage, and a **TailwindCSS frontend**.

It is designed to help small and medium-sized manufacturers manage:
✅ Users and Roles (Admin, Manufacturing Manager, Operator, Inventory Manager)
✅ Bills of Materials (BOM)
✅ Manufacturing Orders (MO)
✅ Work Centers (WC)
✅ Work Orders (WO) and Task Assignments
✅ Inventory and Materials Tracking

---

## 📂 Project Structure

```
CraftERP/
│
├── backend/                  # Backend (Flask API)
│   ├── controllers/          # Business logic for routes
│   ├── models/               # SQLAlchemy / MongoDB schemas
│   ├── routers/              # API route definitions
│   ├── utils/                # Helpers (auth, validators, password hash)
│   ├── database.py           # DB connection (PostgreSQL or MongoDB)
│   └── app.py                # Flask app entry
│
├── frontend/                 # Frontend (HTML + TailwindCSS + JS)
│   ├── bom_create.html       # Create Bill of Material
│   ├── bom_list.html         # List BOMs
│   ├── mo_create.html        # Create Manufacturing Order
│   ├── mo_detail.html        # Manufacturing Order details
│   ├── wo_task.html          # Operator Work Tasks
│   ├── wo_list.html          # List of Work Orders
│   ├── wc_create.html        # Work Center creation
│   ├── user.html             # User management (Admin only)
│   ├── login.html            # Login Page
│   ├── register.html         # Registration Page
│   └── styles.css            # Custom styles (Tailwind)
│
├── create_admin.py           # Seeder script to create admin + sample users
├── README.md                 # 📘 This file
└── requirements.txt          # Python dependencies
```

---

## 🔑 Roles in CraftERP

* **Administrator**
  Full access – manage users, roles, BOMs, WCs, MOs, WOs.

* **Manufacturing Manager**
  Manage BOMs, create Manufacturing Orders, assign Work Orders, manage Work Centers.

* **Operator**
  View and update assigned Work Orders, update task status.

* **Inventory Manager**
  Manage stock of raw materials, BOM components.

---

## ⚙️ Features

### 🔹 User Management

* Admin can **create, update, and view all users**
* Role-based **protected routes** (Admin, Manager, Operator)
* JWT-based authentication & authorization

### 🔹 Bill of Materials (BOM)

* Create BOMs (e.g., Chair → 4 Wood, 12 Screws, 1 Cushion)
* Link BOM to **Work Centers**
* View all BOMs with components

### 🔹 Manufacturing Orders (MO)

* Create MOs based on **BOMs**
* Define **start date, deadline, quantity, assignee**
* Track status: `planned → in_progress → completed`

### 🔹 Work Centers (WC)

* Define production areas (e.g., Cutting, Assembly, Painting)
* Assign BOM operations to WCs

### 🔹 Work Orders (WO)

* Auto-created from Manufacturing Orders
* Assign tasks to Operators
* Operators update task status from **WO Task Page**

### 🔹 Task Tracking

* Operators see **only their tasks** in WO List
* Update status (`pending → in_progress → done`)

---

## 🗄️ Database

CraftERP supports **PostgreSQL (with SQLAlchemy)** and **MongoDB**.

### PostgreSQL Example Schema (`manufacturing_orders`)

```python
class ManufacturingOrder(db.Model):
    __tablename__ = 'manufacturing_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    bom_id = db.Column(db.Integer, db.ForeignKey('bom.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='planned')
    schedule_start = db.Column(db.Date, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
```

### MongoDB Example Schema (`manufacturing_orders`)

```python
manufacturing_order = {
    "bom_id": ObjectId,
    "quantity": 10,
    "status": "planned",
    "schedule_start": datetime,
    "deadline": datetime,
    "assignee_id": ObjectId,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}
```

---

## 🚀 Setup Instructions

### 1️⃣ Clone the Repo

```bash
git clone https://github.com/yourusername/crafterp.git
cd crafterp
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Database

* For **PostgreSQL** → update `SQLALCHEMY_DATABASE_URI` in `backend/database.py`
* For **MongoDB** → update `MONGO_URI` in `backend/database.py`

### 5️⃣ Run Seeder (create admin + sample users)

```bash
python create_admin.py
```

### 6️⃣ Start Flask Server

```bash
cd backend
flask run
```

### 7️⃣ Open Frontend

Navigate to:
👉 `http://127.0.0.1:5000/login.html`

---

## 🧑‍💻 Sample Credentials

| Role                  | Email                                                   | Password     |
| --------------------- | ------------------------------------------------------- | ------------ |
| Admin                 | [admin@cracterp.com](mailto:admin@cracterp.com)         | admin123     |
| Manufacturing Manager | [manager@cracterp.com](mailto:manager@cracterp.com)     | manager123   |
| Operator              | [operator@cracterp.com](mailto:operator@cracterp.com)   | operator123  |
| Inventory Manager     | [inventory@cracterp.com](mailto:inventory@cracterp.com) | inventory123 |

---

## 🎨 Frontend UI

* Built with **Tailwind CSS**
* Hover effects for better UX
* Role-based access for pages

Example Pages:

* `bom_create.html` → Create Bill of Materials
* `mo_create.html` → Create Manufacturing Orders
* `mo_detail.html` → Track Manufacturing Orders
* `wo_task.html` → Operator task updates
* `user.html` → Admin user management

---

## 🔐 Security

* Passwords stored as **hashed values** (bcrypt)
* JWT token authentication
* Role-based route protection
* CSRF safe APIs

---

## 📈 Future Enhancements

* Add **Inventory Management module**
* Generate **Reports (PDF/Excel)**
* Dashboard with charts (production, efficiency, pending tasks)
* Notifications & Alerts (e.g., deadlines, low stock)
* Multi-language support

---

## 🤝 Contributing

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -m "Add new feature"`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create a Pull Request

---

## 📝 License

This project is licensed under the **MIT License** – you are free to use, modify, and distribute.

---

⚡ **CraftERP helps small manufacturers digitalize their process in a simple, modular ERP system.**

