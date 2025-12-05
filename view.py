from flask import Flask, render_template, request, redirect, session, flash
from supabase_client import supabase
import os

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]


# -------------------------------------------------------
# AUTH
# -------------------------------------------------------

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")
    return redirect("/wardrobe")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    from werkzeug.security import generate_password_hash

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        password_hash = generate_password_hash(password)

        result = supabase.table("users").select("*").eq("email", email).execute()
        if result.data:
            flash("There is already an account associated with this email!")
            return render_template("signup.html")

        result = supabase.table("users").insert({
            "email": email,
            "password_hash": password_hash
        }).execute()

        user_id = result.data[0]["id"]

        return redirect("/login")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    from werkzeug.security import check_password_hash

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        result = supabase.table("users").select("*").eq("email", email).execute()
        if not result.data:
            flash("User not found!")
            return render_template("login.html")

        user = result.data[0]

        if not check_password_hash(user["password_hash"], password):
            flash("Incorrect password!")
            return render_template("login.html")

        session["user_id"] = user["id"]
        return redirect("/wardrobe")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# -------------------------------------------------------
# LOAD WARDROBE SUMMARY PAGE
# -------------------------------------------------------

@app.route("/wardrobe")
def wardrobe_home():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    items = supabase.table("items").select("*").eq("user_id", user_id).execute().data
    attributes = supabase.table("item_attributes").select("*").eq("user_id", user_id).execute().data
    rules = supabase.table("rules").select("*").eq("user_id", user_id).execute().data

    return render_template(
        "wardrobe.html",
        items=items,
        attributes=attributes,
        rules=rules
    )


# -------------------------------------------------------
# ITEMS
# -------------------------------------------------------

@app.route("/items")
def list_items():
    user_id = session["user_id"]
    items = supabase.table("items").select("*").eq("user_id", user_id).execute().data
    return render_template("items.html", items=items)


@app.route("/items/new", methods=["GET", "POST"])
def add_item():
    user_id = session["user_id"]

    if request.method == "POST":
        name = request.form["name"]

        attributes = {}  # start empty

        # any custom attribute fields
        for key, value in request.form.items():
            if key.startswith("attr_"):
                attr_name = key.replace("attr_", "")
                attributes[attr_name] = value

        supabase.table("items").insert({
            "user_id": user_id,
            "name": name,
            "attributes": attributes
        }).execute()

        return redirect("/items")

    # fetch attribute definitions for dynamic form
    attrs = supabase.table("item_attributes").select("*").eq("user_id", user_id).execute().data

    return render_template("add_item.html", attributes=attrs)


# -------------------------------------------------------
# ATTRIBUTE DEFINITIONS
# -------------------------------------------------------

@app.route("/attributes")
def list_attributes():
    user_id = session["user_id"]
    attrs = supabase.table("item_attributes").select("*").eq("user_id", user_id).execute().data
    return render_template("attributes.html", attributes=attrs)


@app.route("/attributes/new", methods=["GET", "POST"])
def add_attribute():
    user_id = session["user_id"]

    if request.method == "POST":
        name = request.form["name"]
        type_ = request.form["type"]
        allowed_values = request.form.get("allowed_values", "")

        if allowed_values.strip():
            allowed_values = allowed_values.split(",")
        else:
            allowed_values = None

        supabase.table("item_attributes").insert({
            "user_id": user_id,
            "name": name,
            "type": type_,
            "allowed_values": allowed_values
        }).execute()

        return redirect("/attributes")

    return render_template("add_attribute.html")


# -------------------------------------------------------
# RULES
# -------------------------------------------------------

@app.route("/rules")
def list_rules():
    user_id = session["user_id"]
    rules = supabase.table("rules").select("*").eq("user_id", user_id).execute().data
    return render_template("rules.html", rules=rules)


@app.route("/rules/new", methods=["GET", "POST"])
def add_rule():
    user_id = session["user_id"]

    if request.method == "POST":
        name = request.form["name"]
        type_ = request.form["type"]
        definition = request.form["definition"]  # raw JSON from textarea

        supabase.table("rules").insert({
            "user_id": user_id,
            "name": name,
            "rule_type": type_,
            "definition": supabase.functions.json(definition)
        }).execute()

        return redirect("/rules")

    return render_template("add_rule.html")


# -------------------------------------------------------
# RUN FLASK
# -------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
