# Shipping Document Verifier

This project is a step-by-step implementation for the hackathon participant dataset. We will build it in small, testable stages: input inspection, email classification, attachment extraction, field comparison, reporting, AI integration, and cloud deployment.

## Stage 1: Inspect the input

From `C:\Users\28607\Desktop\hack`, run:

```powershell
python shipping_verifier/inspect_inbox.py --data hac --email email_001
```

The command displays the email subject, body, attachment names, and a preview of text attachments. You can replace the email ID. `--data` may point to any participant dataset containing `inbox/` and `attachments/` directories.

## Target pipeline

```text
JSON email -> classify into five categories -> read SI/BL when required
           -> extract seven fields -> normalize and compare
           -> OK / MISMATCH / NEEDS_REVIEW -> JSON result
```

The seven comparison fields are `shipper`, `consignee`, `notify_party`, `port_of_loading`, `port_of_discharge`, `container_count`, and `gross_weight_kg`.

`NEEDS_REVIEW` means that the system cannot make a reliable decision because information is missing, unreadable, or invalid. Unknown values must not be reported as mismatches. The required output structure is shown in `hac/sample_submission.json`.

## Stage 2: Email classification baseline

```powershell
python shipping_verifier/classify.py --data hac --email email_001
python shipping_verifier/classify.py --data hac --email email_020
```

`classify(email)` returns an immutable `Classification` object containing a typed `Category` and a reason. This initial version is deliberately simple and explainable; it is not the AI integration. It checks the subject before the body because forwarded email bodies may quote older, unrelated messages. Unmatched messages currently fall back to `GENERAL`. We will later route uncertain cases to AI or human review.

Run the focused unit tests with:

```powershell
python -m unittest discover -s shipping_verifier -p "test_*.py" -v
```

## Next stages

### Stage 3: Attachment reading

`read_attachment(data_dir, attachment)` provides one interface for `.txt`, `.pdf`, `.docx`, and `.xlsx` documents. It rejects missing, unsafe, unsupported, and empty attachments explicitly. Install the parsing libraries with `python -m pip install -r shipping_verifier/requirements.txt`.

### Later stages

### Stage 4: Structured field extraction

`ShipmentFields` models the seven values compared between an SI and a draft BL. `extract_fields(text)` extracts multiline party details, ports, container count, and gross weight while accepting the label variants found in the supplied documents. Missing values remain `None` so they can later trigger human review.

### Later stages

1. Normalize extracted values, then compare SI against BL while preserving original values for review.
2. Add AI to classification or extraction, with explicit handling for uncertain results.
3. Build a TypeScript review interface, deploy the application, and complete the documentation and demo.

The supplied event material lists the preliminary submission deadline as **22 September 2026 at 12:00 PM**. Confirm the latest information on the event website before submission.
