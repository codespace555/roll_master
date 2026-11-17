# Roll Master

Roll-wise fabric handling for ERPNext v15 (Sparrow Classics).

Each physical roll = one ERPNext **Batch** (qty in metres).

## What this version contains
- Custom fields (created on install / migrate by `roll_master/install.py`):
  - Item: `custom_category` (Fabric, Trims, Packing, Other) - set Fabric on each fabric item
  - Batch: `custom_tag_id`, `custom_roll_no`, `custom_metres_per_roll`
- API: `roll_master.api.create_rolls`, `roll_master.api.get_rolls`
- Validation: fabric rows on Purchase Receipt / Stock Entry must carry a batch (roll)
- Placeholders (to build next): receipt popup, issue popup, Roll-wise Stock Balance report

## Install (local bench)
```bash
cd frappe-bench
bench get-app /path/to/roll_master        # or the GitHub URL
bench --site <site> install-app roll_master
bench --site <site> migrate
```

## Deploy on Frappe Cloud
1. Push this folder to a private GitHub repo.
2. Bench Group -> Apps -> Add App -> select repo/branch -> Deploy.
3. Site -> Apps -> Install App -> roll_master.
4. Set Category = Fabric on the fabric items.
