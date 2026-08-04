from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from models import Gym
from datetime import datetime
from werkzeug.security import check_password_hash , generate_password_hash
from models import SuperAdmin, db, Gym

super_admin_bp = Blueprint(
    "super_admin",
    __name__
)


# -----------------------------
# Super Admin Login
# -----------------------------
@super_admin_bp.route("/login", methods=["GET", "POST"])
def login():

    # Already Login
    if session.get("super_admin_id"):
        return redirect(url_for("super_admin.dashboard"))

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        admin = SuperAdmin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password, password):

            session["super_admin_id"] = admin.id
            session["super_admin_username"] = admin.username

            flash("Login Successful", "success")

            return redirect(url_for("super_admin.dashboard"))

        flash("Invalid Username or Password", "danger")

    return render_template("super_admin/login.html")


# -----------------------------
# Dashboard
# -----------------------------
@super_admin_bp.route("/dashboard")
def dashboard():

    total_gyms = Gym.query.count()

    active_gyms = Gym.query.filter_by(status="Active").count()

    paused_gyms = Gym.query.filter_by(status="Paused").count()

    premium_gyms = Gym.query.filter_by(plan="Premium").count()

    return render_template(
        "super_admin/dashboard.html",
        total_gyms=total_gyms,
        active_gyms=active_gyms,
        paused_gyms=paused_gyms,
        premium_gyms=premium_gyms,
    )

@super_admin_bp.route("/gyms")
def gyms():

    gyms = Gym.query.all()

    return render_template(
        "super_admin/gyms.html",
        gyms=gyms
    )

@super_admin_bp.route("/add-gym", methods=["GET", "POST"])
def add_gym():

    if request.method == "POST":
        existing_gym = Gym.query.filter_by(
            username=request.form["username"]
        ).first()

        if existing_gym:
            flash("Username already exists.", "danger")
            return render_template("super_admin/add_gym.html")

        gym = Gym(
            gym_name=request.form["gym_name"],
            owner_name=request.form["owner_name"],
            username=request.form["username"],
            password=generate_password_hash(request.form["password"]),
            phone=request.form["phone"],
            email=f"{request.form['username']}@gym.com",   # Temporary
            plan=request.form["plan"],
            plan_expiry_date=datetime.strptime(
                request.form["plan_expiry_date"],
                "%Y-%m-%d"
            ).date(),
            status=request.form["status"],
            reference_by=request.form.get("reference_by")
        )

        db.session.add(gym)
        db.session.commit()

        flash("Gym Added Successfully", "success")

        return redirect(url_for("super_admin.gyms"))

    return render_template("super_admin/add_gym.html")

@super_admin_bp.route("/pause-gym/<int:id>")
def pause_gym(id):

    gym = Gym.query.get_or_404(id)

    if gym.status == "Active":

        gym.status = "Paused"
        flash("Gym Paused Successfully", "warning")

    else:

        gym.status = "Active"
        flash("Gym Activated Successfully", "success")

    db.session.commit()

    return redirect(url_for("super_admin.gyms"))

@super_admin_bp.route("/view-gym/<int:id>")
def view_gym(id):

    gym = Gym.query.get_or_404(id)

    return render_template(
        "super_admin/view_gym.html",
        gym=gym
    )


@super_admin_bp.route("/edit-gym/<int:id>", methods=["GET", "POST"])
def edit_gym(id):

    gym = Gym.query.get_or_404(id)

    if request.method == "POST":

        gym.gym_name = request.form["gym_name"]
        gym.owner_name = request.form["owner_name"]
        gym.username = request.form["username"]
        gym.phone = request.form["phone"]
        gym.plan = request.form["plan"]
        gym.status = request.form["status"]
        gym.reference_by = request.form.get("reference_by")

        gym.plan_expiry_date = datetime.strptime(
            request.form["plan_expiry_date"],
            "%Y-%m-%d"
        ).date()

        # Password tabhi change hoga jab naya password diya ho
        if request.form["password"] != "":
            gym.password = generate_password_hash(
                request.form["password"]
            )

        db.session.commit()

        flash("Gym Updated Successfully", "success")

        return redirect(url_for("super_admin.gyms"))

    return render_template(
        "super_admin/edit_gym.html",
        gym=gym
    )

@super_admin_bp.route("/delete-gym/<int:id>")
def delete_gym(id):

    gym = Gym.query.get_or_404(id)

    db.session.delete(gym)

    db.session.commit()

    flash("Gym Deleted Successfully", "success")

    return redirect(url_for("super_admin.gyms"))


# -----------------------------
# Logout
# -----------------------------
@super_admin_bp.route("/logout")
def logout():

    session.pop("super_admin_id", None)
    session.pop("super_admin_username", None)

    flash("Logged Out Successfully", "success")

    return redirect(url_for("super_admin.login"))