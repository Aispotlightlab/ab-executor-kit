#!/usr/bin/env python3
"""OPP-0006 — Alberta lay-executor estate kit generator (stdlib only).

Produces dist/alberta-executor-kit/*.csv + README.md: a dated task checklist, an expense/reimbursement
ledger, an asset inventory and a distribution sheet. Organizer only — no legal advice (see DISCLAIMER).
Run: python3 build_kit.py [death_date YYYY-MM-DD]
"""
import csv, os, sys
from datetime import date, timedelta

DISCLAIMER = ("This kit is an organizer, not legal advice. Executor duties in Alberta are governed by the "
              "Estate Administration Act and the Surrogate Rules; confirm deadlines with a lawyer or the "
              "Court of King's Bench Surrogate office.")

# (offset_days_from_death, phase, task) — order is the typical Alberta sequence; offsets are planning
# defaults for the executor's own calendar, not statutory deadlines unless marked [statutory].
TASKS = [
    (0, "First week", "Obtain the Funeral Director's Statement of Death (several copies)"),
    (0, "First week", "Locate the original will; note any codicils"),
    (2, "First week", "Secure the residence, vehicles, valuables; notify insurer the home is vacant if so"),
    (7, "First week", "Apply for Vital Statistics death certificate (Alberta Registry agent)"),
    (7, "First month", "Notify CPP (death benefit + survivor), OAS, employer, pension plans"),
    (14, "First month", "Open an estate bank account; stop automatic payments; redirect mail (Canada Post)"),
    (14, "First month", "Notify Service Canada, CRA (deceased's SIN), Alberta Health, driver licence"),
    (21, "First month", "Inventory assets and debts (use 02-assets.csv); request date-of-death balances"),
    (30, "Month 1-3", "Decide whether a Grant of Probate/Administration is needed (bank/land-title thresholds)"),
    (45, "Month 1-3", "Prepare Surrogate forms (NC-series) and serve notices on beneficiaries [statutory: before filing]"),
    (60, "Month 1-3", "File probate application at Court of King's Bench; pay court fee by estate value"),
    (90, "Month 3-6", "Publish/consider NoticeConnect or newspaper notice to creditors (optional, protective)"),
    (120, "Month 3-6", "Sell or transfer real property; vehicles; close accounts into the estate account"),
    (150, "Month 3-6", "File the deceased's final T1 (due Apr 30 of next year, or 6 months after death if later) [statutory]"),
    (180, "Month 6-12", "File T3 trust return for estate income if any; request CRA clearance certificate"),
    (270, "Month 6-12", "Prepare the estate accounting (use 01-expenses.csv + 03-distributions.csv) for beneficiaries"),
    (300, "Month 6-12", "Obtain releases from beneficiaries or pass accounts through the court"),
    (330, "Month 6-12", "Distribute the residue; keep records 7 years"),
]

EXPENSE_HEADER = ["date", "paid_by", "payee", "category", "amount_cad", "reimbursed_on", "receipt_ref", "notes"]
EXPENSE_CATS = "funeral | court fee | probate legal | accounting | property upkeep | utilities | travel | postage | other"
ASSET_HEADER = ["asset", "type", "institution_or_location", "account_or_ref", "date_of_death_value_cad",
                "joint_or_beneficiary_designated", "status", "notes"]
DIST_HEADER = ["beneficiary", "share_per_will", "interim_paid_cad", "final_paid_cad", "release_signed_on", "notes"]


def build(death: date, out: str) -> list[str]:
    os.makedirs(out, exist_ok=True)
    written = []

    p = os.path.join(out, "00-task-checklist.csv")
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["target_date", "phase", "task", "done", "notes"])
        for off, phase, task in TASKS:
            w.writerow([(death + timedelta(days=off)).isoformat(), phase, task, "", ""])
    written.append(p)

    for name, header, example in [
        ("01-expenses.csv", EXPENSE_HEADER, [death.isoformat(), "executor", "Funeral home", "funeral", "", "", "", EXPENSE_CATS]),
        ("02-assets.csv", ASSET_HEADER, ["Chequing account", "bank", "", "", "", "no", "open", ""]),
        ("03-distributions.csv", DIST_HEADER, ["", "", "", "", "", ""]),
    ]:
        p = os.path.join(out, name)
        with open(p, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerow(example)
        written.append(p)

    p = os.path.join(out, "README.md")
    with open(p, "w") as f:
        f.write("# Alberta Executor Kit\n\n")
        f.write(f"Generated for date of death {death.isoformat()}.\n\n")
        f.write("Files: 00-task-checklist.csv (dated), 01-expenses.csv (claim reimbursement from the estate), "
                "02-assets.csv (date-of-death inventory), 03-distributions.csv.\n\n")
        f.write("One-time purchase, no subscription, nothing to cancel. Plain CSV: opens in Excel, Numbers, "
                "Google Sheets or LibreOffice and stays yours offline.\n\n")
        f.write(f"DISCLAIMER: {DISCLAIMER}\n")
    written.append(p)
    return written


def bundle(files: list[str], zip_path: str) -> str:
    """Pack the generated kit into one zip — the file a buyer downloads after checkout."""
    import zipfile
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, arcname=os.path.join("alberta-executor-kit", os.path.basename(p)))
    return zip_path


def _selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        files = build(date(2026, 1, 15), d)
        assert len(files) == 5, files
        rows = list(csv.reader(open(os.path.join(d, "00-task-checklist.csv"))))
        assert rows[0][0] == "target_date" and len(rows) == len(TASKS) + 1
        assert rows[1][0] == "2026-01-15" and rows[-1][0] == "2026-12-11"
        readme = open(os.path.join(d, "README.md")).read()
        assert "not legal advice" in readme and "no subscription" in readme
        import zipfile
        zp = bundle(files, os.path.join(d, "kit.zip"))
        names = zipfile.ZipFile(zp).namelist()
        assert len(names) == 5 and all(n.startswith("alberta-executor-kit/") for n in names), names
    print("selftest ok: 5 files, %d tasks, dates sorted, zip bundle 5 entries" % len(TASKS))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        _selftest()
    else:
        death = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
        dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
        files = build(death, os.path.join(dist, "alberta-executor-kit"))
        for p in files:
            print(p)
        print(bundle(files, os.path.join(dist, "alberta-executor-kit.zip")))
