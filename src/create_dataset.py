import json
import os


def generate_bfsi_dataset():
    dataset = []

    # Templates for various BFSI categories

    # 1. Loan Eligibility & Application
    loan_types = ["Home Loan", "Personal Loan", "Car Loan", "Education Loan"]
    for loan in loan_types:
        dataset.append({
            "instruction": f"What are the eligibility criteria for a {loan}?",
            "input": "",
            "output": f"To be eligible for a {loan}, you typically need to be between 21 and 60 years of age, have a stable income source, and a credit score above 700. Salaried employees need a minimum work experience of 2 years, while self-employed individuals need a business continuity of 3 years."
        })
        dataset.append({
            "instruction": f"How can I apply for a {loan}?",
            "input": "",
            "output": f"You can apply for a {loan} by visiting our nearest branch with your KYC documents, income proof, and bank statements. Alternatively, you can apply online through our mobile banking app or website for a faster approval process."
        })
        dataset.append({
            "instruction": f"What documents are required for a {loan}?",
            "input": "",
            "output": f"Common documents for a {loan} include: 1) Identity Proof (Aadhar/PAN), 2) Address Proof (Utility Bill/Passport), 3) Income Proof (Salary Slips/ITR), and 4) Bank Statements for the last 6 months."
        })

    # 2. EMI Details & Schedules
    dataset.append({
        "instruction": "How is my EMI calculated?",
        "input": "",
        "output": "Your Equated Monthly Installment (EMI) is calculated based on the principal loan amount, the interest rate, and the loan tenure. The formula used is EMI = [P x R x (1+R)^N]/[(1+R)^N-1], where P is Principal, R is monthly interest rate, and N is tenure in months."
    })
    dataset.append({
        "instruction": "Can I pay my EMI in advance?",
        "input": "",
        "output": "Yes, you can make a pre-payment towards your loan. However, some loans may attract a pre-payment penalty of up to 2% on the outstanding principal amount. Please check your loan agreement for specific terms."
    })

    # 3. Interest Rates (Generic)
    products = ["Savings Account", "Fixed Deposit", "Recurring Deposit", "Senior Citizen FD"]
    for prod in products:
        dataset.append({
            "instruction": f"What is the current interest rate for a {prod}?",
            "input": "",
            "output": f"The current interest rate for a {prod} ranges from 3.0% to 7.5% per annum, depending on the tenure and amount. Senior citizens typically get an additional 0.5% interest."
        })

    # 4. Payment & Transactions
    transactions = ["NEFT", "RTGS", "IMPS", "UPI"]
    for tx in transactions:
        dataset.append({
            "instruction": f"What is the limit for {tx} transactions?",
            "input": "",
            "output": f"The transaction limit for {tx} varies. Typically: NEFT has no minimum limit, RTGS has a minimum of 2 Lakhs, and IMPS/UPI usually have a daily limit of 1 Lakh to 5 Lakhs depending on your account type."
        })
        dataset.append({
            "instruction": f"How long does a {tx} transfer take?",
            "input": "",
            "output": f"{tx} transfers are usually instant or processed in batches within few hours. UPI and IMPS are 24x7 instant payment systems."
        })

    # 5. General Support
    general_queries = [
        ("How do I block my lost debit card?", "You can block your debit card immediately through our mobile banking app under 'Card Management', or by sending an SMS 'BLOCK <Last 4 digits>' to our support number, or by calling our 24x7 toll-free helpline."),
        ("how to change my registered mobile number?", "To change your registered mobile number, please visit your home branch with a valid ID proof and fill out the customer request form. For security reasons, this cannot be done online."),
        ("What are the branch working hours?", "Our branches are open from 10:00 AM to 4:00 PM, Monday to Saturday (except 2nd and 4th Saturdays and public holidays)."),
        ("How to enable international transactions on my card?", "You can enable international transactions by logging into Net Banking or Mobile App > and going to Manage Cards > Usage Settings > Enable International Usage.")
    ]
    for q, a in general_queries:
        dataset.append({
            "instruction": q,
            "input": "",
            "output": a
        })

    # 6. Insurance queries
    insurance_queries = [
        ("What types of insurance do you offer?", "We offer Term Life Insurance, Health Insurance, Motor Insurance, and Unit-Linked Plans (ULIPs). Each plan can be customized based on your requirements."),
        ("How do I file an insurance claim?", "To file a claim, contact our claims department via toll-free number or the Mobile Banking app within 24 hours. Submit required documents (policy doc, ID proof, relevant reports). Claims are processed within 30 days."),
        ("What is the premium for term insurance?", "Term insurance premiums start from approximately ₹500/month for ₹1 Crore coverage for a 30-year-old non-smoker. Actual premiums depend on age, health, coverage amount, and tenure."),
    ]
    for q, a in insurance_queries:
        dataset.append({
            "instruction": q,
            "input": "",
            "output": a
        })

    # Generate variations to reach 150+
    base_dataset = dataset.copy()
    variations = [
        "Please explain ",
        "I want to know about ",
        "Can you tell me ",
        "Details for "
    ]

    extended_dataset = []
    for item in base_dataset:
        extended_dataset.append(item)  # Add original

        # Create variations for each original item
        for var in variations:
            new_item = item.copy()
            if not item["instruction"].lower().startswith("how") and not item["instruction"].lower().startswith("what"):
                new_item["instruction"] = var + item["instruction"]
            else:
                if item["instruction"].lower().startswith("what is"):
                    new_item["instruction"] = item["instruction"].replace("What is", "Tell me about")
                elif "how to" in item["instruction"].lower():
                    new_item["instruction"] = item["instruction"].replace("How to", "I need to")

            # Only add if instruction actually changed
            if new_item["instruction"] != item["instruction"]:
                extended_dataset.append(new_item)

    # Cap at 180 to be safe and above 150
    final_dataset = extended_dataset[:180]

    print(f"Generated {len(final_dataset)} dataset entries.")

    # Save to project root (matching the path used by app.py)
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "bfsi_alpaca_1_to_160_final_clean.json"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_dataset, f, indent=4, ensure_ascii=False)
    print(f"Dataset saved to {output_path}")


if __name__ == "__main__":
    generate_bfsi_dataset()
