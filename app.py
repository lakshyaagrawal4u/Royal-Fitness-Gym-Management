from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Admin, Member, Payment
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import quote


app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = "royalfitness123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gym.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database
db.init_app(app)

# Create Database Tables & Default Admin
with app.app_context():

    db.create_all()

    admin = Admin.query.filter_by(username="admin").first()

    if not admin:

        admin = Admin(
            username="admin",
            password=generate_password_hash("admin123")
        )

        db.session.add(admin)
        db.session.commit()

        print("✅ Default Admin Created")

def get_due_members():

    due_list = []

    today = date.today()

    members = Member.query.all()

    for member in members:

        # ----------------------------
        # Fee Paid Till ya Joining Date
        # ----------------------------

        if member.last_fee_paid:
            last_payment = member.last_fee_paid
            next_due = member.last_fee_paid + relativedelta(months=1)
        else:
            last_payment = None
            next_due = member.joining_date + relativedelta(months=1)

        # ----------------------------
        # Due Check
        # ----------------------------

        if today >= next_due:

            # Pending Months
            pending_months = relativedelta(today, next_due)

            months = (
                pending_months.years * 12
                + pending_months.months
                + 1
            )

            overdue_days = (today - next_due).days

            due_list.append({

                "member": member,

                "last_payment": last_payment,

                "next_due": next_due,

                "pending_months": months,

                "overdue_days": overdue_days

            })

    return due_list


# Home Route
@app.route("/")
def home():
    return render_template("index.html")



@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password, password):

            session["admin"] = admin.username

            return redirect(url_for("dashboard"))

        flash("Invalid Username or Password")

    return render_template("login.html")

@app.route("/change_password", methods=["GET", "POST"])
def change_password():

    if "admin" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        admin = Admin.query.filter_by(username=session["admin"]).first()

        # Current password check
        if not check_password_hash(admin.password, current_password):
            flash("Current password is incorrect!", "danger")
            return redirect(url_for("change_password"))

        # New password match
        if new_password != confirm_password:
            flash("New passwords do not match!", "danger")
            return redirect(url_for("change_password"))

        # Minimum length
        if len(new_password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return redirect(url_for("change_password"))

        # Save new password
        admin.password = generate_password_hash(new_password)

        db.session.commit()

        flash("Password changed successfully!", "success")

        return redirect(url_for("dashboard"))

    return render_template("change_password.html")

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect(url_for("login"))

    total_members = Member.query.count()

    total_collection = db.session.query(
        db.func.sum(Payment.amount)
    ).filter(
        Payment.payment_date == date.today()
    ).scalar() or 0

    due_list = get_due_members()
    due_count = len(due_list)

    return render_template(
        "dashboard.html",
        total_members=total_members,
        total_collection=total_collection,
        due_members=due_count
    )

@app.route("/add_member", methods=["GET", "POST"])
def add_member():

    if "admin" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        try:

            phone = request.form["phone"].strip()
            age = int(request.form["age"])
            monthly_fee = float(request.form["fee"])

            # -------- Mobile Validation --------

            if not phone.isdigit() or len(phone) != 10:
                flash("Please enter a valid 10-digit mobile number.", "danger")
                return redirect(url_for("add_member"))

            # -------- Duplicate Mobile --------

            existing_member = Member.query.filter_by(phone=phone).first()

            if existing_member:
                flash("This mobile number is already registered.", "danger")
                return redirect(url_for("add_member"))

            # -------- Age Validation --------

            if age < 10 or age > 100:
                flash("Age must be between 10 and 100.", "danger")
                return redirect(url_for("add_member"))

            # -------- Fee Validation --------

            if monthly_fee <= 0:
                flash("Monthly fee must be greater than 0.", "danger")
                return redirect(url_for("add_member"))

            # -------- Last Fee Paid --------

            last_fee_paid = None

            if request.form["last_fee_paid"]:
                last_fee_paid = datetime.strptime(
                    request.form["last_fee_paid"],
                    "%Y-%m-%d"
                ).date()

            # -------- Create Member --------

            member = Member(

                name=request.form["name"].strip(),
                phone=phone,
                age=age,
                gender=request.form["gender"],
                address=request.form["address"].strip(),

                joining_date=datetime.strptime(
                    request.form["joining_date"],
                    "%Y-%m-%d"
                ).date(),

                last_fee_paid=last_fee_paid,

                membership_plan=request.form["plan"],
                trainer=request.form["trainer"].strip(),
                monthly_fee=monthly_fee,
                status="Active"
            )

            db.session.add(member)
            db.session.commit()

            flash("Member Added Successfully!", "success")

            return redirect(url_for("add_member"))

        except Exception as e:

            db.session.rollback()

            print(e)

            flash("Something went wrong while adding the member.", "danger")

            return redirect(url_for("add_member"))

    return render_template("add_member.html")


from sqlalchemy import or_

@app.route("/members")
def members():

    if "admin" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()

    if search:

        all_members = Member.query.filter(

            or_(
                Member.name.ilike(f"%{search}%"),
                Member.phone.ilike(f"%{search}%")
            )

        ).all()

    else:

        all_members = Member.query.all()

    return render_template(
        "members.html",
        members=all_members,
        search=search
    )

@app.route("/edit_member/<int:id>", methods=["GET", "POST"])
def edit_member(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    member = Member.query.get_or_404(id)

    if request.method == "POST":

        try:

            phone = request.form["phone"].strip()
            age = int(request.form["age"])
            monthly_fee = float(request.form["fee"])

            # -------- Mobile Validation --------

            if not phone.isdigit() or len(phone) != 10:
                flash("Please enter a valid 10-digit mobile number.", "danger")
                return redirect(url_for("edit_member", id=id))

            # -------- Duplicate Mobile Check --------

            existing_member = Member.query.filter(
                Member.phone == phone,
                Member.id != id
            ).first()

            if existing_member:
                flash("This mobile number is already registered.", "danger")
                return redirect(url_for("edit_member", id=id))

            # -------- Age Validation --------

            if age < 10 or age > 100:
                flash("Age must be between 10 and 100.", "danger")
                return redirect(url_for("edit_member", id=id))

            # -------- Fee Validation --------

            if monthly_fee <= 0:
                flash("Monthly fee must be greater than 0.", "danger")
                return redirect(url_for("edit_member", id=id))

            # -------- Update Member --------

            member.name = request.form["name"].strip()
            member.phone = phone
            member.age = age
            member.gender = request.form["gender"]
            member.address = request.form["address"].strip()

            member.joining_date = datetime.strptime(
                request.form["joining_date"],
                "%Y-%m-%d"
            ).date()

            member.last_fee_paid = (
                datetime.strptime(
                    request.form["last_fee_paid"],
                    "%Y-%m-%d"
                ).date()
                if request.form["last_fee_paid"]
                else None
            )

            member.membership_plan = request.form["plan"]
            member.trainer = request.form["trainer"].strip()
            member.monthly_fee = monthly_fee

            db.session.commit()

            flash("Member Updated Successfully!", "success")

            return redirect(url_for("members"))

        except Exception as e:

            db.session.rollback()
            print(e)

            flash("Something went wrong while updating the member.", "danger")

            return redirect(url_for("edit_member", id=id))

    return render_template("edit_member.html", member=member)


@app.route("/delete_member/<int:id>")
def delete_member(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    try:

        member = Member.query.get_or_404(id)

        db.session.delete(member)
        db.session.commit()

        flash("Member Deleted Successfully!", "success")

    except Exception as e:

        db.session.rollback()
        print(e)

        flash("Unable to delete member.", "danger")

    return redirect(url_for("members"))


@app.route("/pay_fee/<int:id>", methods=["GET", "POST"])
def pay_fee(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    member = Member.query.get_or_404(id)

    # -------------------------
    # Pending Months Calculate
    # -------------------------

    today = date.today()

    if member.last_fee_paid:
        next_due = member.last_fee_paid + relativedelta(months=1)
    else:
        next_due = member.joining_date + relativedelta(months=1)

    if today >= next_due:
        diff = relativedelta(today, next_due)
        pending_months = diff.years * 12 + diff.months + 1
    else:
        pending_months = 1      # Advance Payment Allowed

    if request.method == "POST":

        try:

            months_paid = int(request.form["months_paid"])

            # -------- Validation --------

            if months_paid <= 0:
                flash("Months paid must be greater than 0.", "danger")
                return redirect(url_for("pay_fee", id=id))

            payment_date = date.fromisoformat(
                request.form["payment_date"]
            )

            amount = member.monthly_fee * months_paid

            payment = Payment(

                member_id=member.id,

                amount=amount,

                payment_date=payment_date,

                months_paid=months_paid,

                payment_mode=request.form["payment_mode"],

                remarks=request.form["remarks"].strip()

            )

            db.session.add(payment)

            # -------------------------
            # Update Fee Paid Till
            # -------------------------

            if member.last_fee_paid:

                member.last_fee_paid = (
                    member.last_fee_paid
                    + relativedelta(months=months_paid)
                )

            else:

                member.last_fee_paid = (
                    member.joining_date
                    + relativedelta(months=months_paid)
                )

            db.session.commit()

            flash("Payment Added Successfully!", "success")

            return redirect(url_for("members"))

        except Exception as e:

            db.session.rollback()

            print(e)

            flash("Something went wrong while saving the payment.", "danger")

            return redirect(url_for("pay_fee", id=id))

    return render_template(

        "pay_fee.html",

        member=member,

        today=today,

        next_due=next_due,

        pending_months=pending_months,

        total_amount=member.monthly_fee * pending_months

    )



@app.route("/send_reminder/<int:id>")
def send_reminder(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    member = Member.query.get_or_404(id)

    today = date.today()

    if member.last_fee_paid:
        next_due = member.last_fee_paid + relativedelta(months=1)
    else:
        next_due = member.joining_date + relativedelta(months=1)

    overdue_days = max((today - next_due).days, 0)

    message = f"""
Hello {member.name},

🏋️ Royal Fitness Reminder

Your gym membership fee is pending.

💰 Monthly Fee : ₹{member.monthly_fee}

📅 Due Since : {overdue_days} day(s)

Kindly pay your membership fee.

Thank you!
Royal Fitness
"""

    whatsapp_url = (
        f"https://wa.me/91{member.phone}"
        f"?text={quote(message)}"
    )

    return redirect(whatsapp_url)

@app.route("/payments")
def payments():

    if "admin" not in session:
        return redirect(url_for("login"))

    payments = db.session.query(Payment, Member)\
        .join(Member, Payment.member_id == Member.id)\
        .order_by(Payment.payment_date.desc())\
        .all()

    return render_template(
        "payments.html",
        payments=payments
    )

@app.route("/due_members")
def due_members():

    if "admin" not in session:
        return redirect(url_for("login"))

    due_list = get_due_members()

    return render_template(
    "due_members.html",
    due_members=due_list
)

@app.route("/logout")
def logout():

    session.pop("admin", None)

    flash("Logged out successfully.", "success")

    return redirect(url_for("home"))

# -----------------------------
# Error Handlers
# -----------------------------

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template("500.html"), 500

@app.route("/check_admin")
def check_admin():

    admins = Admin.query.all()

    return {
        "count": len(admins),
        "admins": [a.username for a in admins]
    }


if __name__ == "__main__":
    app.run(debug=True)


