# =============================
# Dinner Wheel – Flask App
# =============================

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import datetime
import os

from main import (
    action_spin,
    action_respin,
    action_finalize,
    maybe_auto_finalize_today,
    get_session_events_for_date,
    get_current_dinner_for_date,
    get_final_dinner_for_date,
    get_dinner_statistics,
    get_all_dinners_from_db,
    get_last_n_final_dinners,
    add_dinner_to_list,
    remove_dinner_from_list,
    STEFFEN,
    SABRINA
)

app = Flask(__name__)
app.secret_key = "supersecretkey"


def get_today_str():
    return datetime.date.today().strftime("%d-%m-%Y")


def find_dinner_image(dinner_name):
    """
    Looks in static/images/ for an image matching the dinner name.
    Tries an exact match first, then a lowercased/underscored version.
    Returns just the filename (e.g. 'pasta_carbonara.jpg') or None.
    """
    if not dinner_name:
        return None

    images_dir = os.path.join(app.static_folder, "images")
    if not os.path.isdir(images_dir):
        return None

    # Candidates to try, in order of preference
    candidates = [
        dinner_name + ".jpg",
        dinner_name + ".png",
        dinner_name.lower().replace(" ", "_") + ".jpg",
        dinner_name.lower().replace(" ", "_") + ".png",
        dinner_name.lower() + ".jpg",
        dinner_name.lower() + ".png",
    ]

    existing = {f.lower(): f for f in os.listdir(images_dir)}

    for candidate in candidates:
        if candidate.lower() in existing:
            return existing[candidate.lower()]

    return None


@app.route("/")
def index():
    todaysDate  = get_today_str()
    dinners     = get_all_dinners_from_db()
    current     = get_current_dinner_for_date(todaysDate)
    final       = get_final_dinner_for_date(todaysDate)
    image       = find_dinner_image(current)
    last_dinners = get_last_n_final_dinners(5)   # list of (date, dinner)
    stats       = get_dinner_statistics()         # list of (dinner, count)

    return render_template(
        "index.html",
        dinners=dinners,
        current=current,
        final=final,
        image=image,
        last_dinners=last_dinners,
        stats=stats
    )


# ------------------------------------------------------------------
# JSON endpoint for initial spin
# ------------------------------------------------------------------
@app.route("/api/spin")
def api_spin():
    success, message, dinner = action_spin()
    maybe_auto_finalize_today()
    image = find_dinner_image(dinner)
    return jsonify({"success": success, "message": message, "dinner": dinner, "image": image})


# ------------------------------------------------------------------
# JSON endpoint for respin — same pattern as api_spin
# ------------------------------------------------------------------
@app.route("/api/respin/<person>")
def api_respin(person):
    if person == "steffen":
        success, message, dinner = action_respin(STEFFEN)
    elif person == "sabrina":
        success, message, dinner = action_respin(SABRINA)
    else:
        return jsonify({"success": False, "message": "Unknown person", "dinner": None, "image": None})

    maybe_auto_finalize_today()
    image = find_dinner_image(dinner)
    return jsonify({"success": success, "message": message, "dinner": dinner, "image": image})


@app.route("/finalize")
def finalize():
    success, message, dinner = action_finalize()
    flash(message)
    return redirect(url_for("index"))


@app.route("/add_dinner", methods=["POST"])
def add_dinner():
    dinner = request.form.get("dinner", "").strip()
    if not dinner:
        flash("Please enter a valid dinner name")
    else:
        add_dinner_to_list(dinner)
        flash(f"✔ {dinner} added to the list")
    return redirect(url_for("index"))


@app.route("/remove_dinner/<int:index>")
def remove_dinner(index):
    success, message = remove_dinner_from_list(index)
    flash(message)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)






# =============================
# Maintain Unavailability
# =============================