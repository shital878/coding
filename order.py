import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
from db_config import DB_CONFIG

# from io import BytesIO
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet


def order_details():

        # ---------------- PAGE CONFIG ----------------
    st.set_page_config(page_title="Outlet Management System", layout="wide")

    # ---------------- CUSTOM CSS ----------------
    st.markdown("""
<style>

/* Main Background */

[data-testid="stAppViewContainer"]{
background: linear-gradient(to right,#d6eaf8,#f9ebea);
}

/* Center Title */

.main-title{
font-size:40px;
font-weight:bold;
text-align:center;
color:#154360;
margin-bottom:25px;
}

/* Card Design */

.card{
background:white;
padding:30px;
border-radius:12px;
box-shadow:0px 4px 12px rgba(0,0,0,0.15);
margin-bottom:20px;
}

/* Text Input */

div[data-baseweb="input"] > div{
background-color:#fdfefe;
border:2px solid #2E86C1;
border-radius:8px;
}

div[data-baseweb="input"] > div:focus-within{
border:2px solid #1B4F72;
background-color:#EBF5FB;
}

/* Labels */

label{
color:#154360 !important;
font-weight:600;
}

 /* Buttons */

.stButton > button,
div[data-testid="stFormSubmitButton"] > button{
background:#28B463;
color:white;
border-radius:8px;
height:42px;
width:200px;
font-weight:bold;
border:none;
}

/* Hover */

.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover{
background:#1D8348;
color:white;
}

/* Sidebar */

section[data-testid="stSidebar"]{
background-color:#F8C471;
}

</style>
""", unsafe_allow_html=True)

    # ---------------- TITLE ----------------
    st.markdown('<div class="main-title">Outlet Management System</div>', unsafe_allow_html=True)


    st.header("Order Master")

    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    menu = st.sidebar.radio("Order", ["Order","Update","Delivery","Bill"])
    query = "SELECT * FROM masala_master"
    df = pd.read_sql(query, connection)

    # Load Customer Master
    cust_query = "SELECT shop_name FROM customer"
    cust_df = pd.read_sql(cust_query, connection)


    # ================= ORDER PAGE =================
    if menu == "Order":

        cust_name = st.selectbox("Select Customer", cust_df["shop_name"])

        # Initialize storage
        if "order_values" not in st.session_state:
            st.session_state.order_values = {}

        # Search box
        search_text = st.text_input("🔍 Search Masala")

        # Filter dataframe
        if search_text:
            filtered_df = df[
                df["masala_name"].str.contains(search_text, case=False, na=False)
            ]
        else:
            filtered_df = df

        st.subheader("Enter Order Details")

        # Header
        h1, h2, h3 = st.columns([2,1,1])

        h1.markdown("**Masala Name**")
        h2.markdown("**Qty**")
        h3.markdown("**Rate**")

        # ================= DISPLAY ITEMS =================
        for index, row in filtered_df.iterrows():

            masala_id = str(row["id"])
            masala_name = row["masala_name"]

            # Create storage if not exists
            if masala_id not in st.session_state.order_values:

                st.session_state.order_values[masala_id] = {
                    "name": masala_name,
                    "qty": 0,
                    "rate": 0
                }

            col1, col2, col3 = st.columns([2,1,1])

            col1.text_input(
                "",
                value=masala_name,
                disabled=True,
                key=f"name_{masala_id}"
            )

            qty = col2.number_input(
                "",
                min_value=0,
                value=st.session_state.order_values[masala_id]["qty"],
                key=f"qty_{masala_id}"
            )

            rate = col3.number_input(
                "",
                min_value=0,
                value=st.session_state.order_values[masala_id]["rate"],
                key=f"rate_{masala_id}"
            )

            # Save latest values
            st.session_state.order_values[masala_id]["qty"] = qty
            st.session_state.order_values[masala_id]["rate"] = rate

        # ================= SUBMIT =================
        if st.button("Submit Order"):

            inserted = False
            error_found = False

            cursor = connection.cursor()

            for masala_id, data in st.session_state.order_values.items():

                masala_name = data["name"]
                qty = data["qty"]
                rate = data["rate"]

                amount = qty * rate

                # Skip empty rows
                if qty == 0 and rate == 0:
                    continue

                if qty <= 0:
                    st.error(f"Quantity must be greater than 0 for {masala_name}")
                    error_found = True
                    continue

                if rate <= 0:
                    st.error(f"Rate must be greater than 0 for {masala_name}")
                    error_found = True
                    continue

                # Duplicate check
                check_query = """
                SELECT COUNT(*)
                FROM masala_order
                WHERE cust_name = %s
                AND masala_name = %s
                AND business_date = CURRENT_DATE
                """

                cursor.execute(check_query, (cust_name, masala_name))

                count = cursor.fetchone()[0]

                if count > 0:

                    st.warning(f"{masala_name} already ordered today")

                else:

                    insert_query = """
                    INSERT INTO masala_order
                    (id, cust_name, masala_name, qty, rate, amount,
                     business_date, order_time)
                    VALUES (%s, %s, %s, %s, %s, %s,
                            CURRENT_DATE, CURRENT_TIMESTAMP)
                    """

                    cursor.execute(
                        insert_query,
                        (
                            masala_id,
                            cust_name,
                            masala_name,
                            qty,
                            rate,
                            amount
                        )
                    )

                    inserted = True

            if not error_found:
                connection.commit()

            if inserted:
                st.success("Order Inserted Successfully")

                # Clear session after submit
                st.session_state.order_values = {}

    # # ================= ORDER PAGE =================
    # if menu == "Order":

    #     cust_name = st.selectbox("Select Customer", cust_df["shop_name"])


    #     # 🔍 Search Box
    #     search_text = st.text_input("🔍 Search Masala")


    #     with st.form("order_form", clear_on_submit=True):

    #         st.subheader("Enter Order Details")

    #         # Table Header
    #         h1, h2, h3 = st.columns([1.5,1,1])
    #         h1.markdown("**Masala Name**")
    #         h2.markdown("**Qty**")
    #         h3.markdown("**Rate**")

    #         order_data = []

    #         for index, row in filtered_df.iterrows():

    #             masala_id = row["id"]
    #             masala_name = row["masala_name"]



    #             col1, col2, col3 = st.columns([1.5,1,1])

    #             col1.text_input(
    #                 "",
    #                 value=masala_name,
    #                 disabled=True,
    #                 key=f"name_{masala_id}"
    #             )

    #             qty = col2.number_input("", min_value=0, key=f"qty_{masala_id}")
    #             rate = col3.number_input("", min_value=0, key=f"rate_{masala_id}")

    #             amount = qty * rate

    #             order_data.append((masala_id, masala_name, qty, rate, amount))

    #         # Submit button OUTSIDE loop
    #         submit = st.form_submit_button("Submit Order")


    #     if submit:

    #         cursor = connection.cursor()

    #         inserted = False
    #         error_found = False

    #         for data in order_data:

    #             masala_id, masala_name, qty, rate, amount = data

    #             # Skip empty rows
    #             if qty == 0 and rate == 0:
    #                 continue

    #             # Qty validation
    #             if qty <= 0:
    #                 st.error(f"Quantity must be greater than 0 for {masala_name}")
    #                 error_found = True
    #                 continue

    #             # Rate validation
    #             if rate <= 0:
    #                 st.error(f"Rate must be greater than 0 for {masala_name}")
    #                 error_found = True
    #                 continue

    #             # Duplicate check
    #             check_query = """
    #             SELECT COUNT(*)
    #             FROM masala_order
    #             WHERE cust_name = %s
    #             AND masala_name = %s
    #             AND business_date = CURRENT_DATE
    #             """

    #             cursor.execute(check_query, (cust_name, masala_name))
    #             count = cursor.fetchone()[0]

    #             if count > 0:

    #                 st.warning(f"{masala_name} already ordered today")

    #             else:

    #                 insert_query = """
    #                 INSERT INTO masala_order
    #                 (id, cust_name, masala_name, qty, rate, amount, business_date, order_time)
    #                 VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE, CURRENT_TIMESTAMP)
    #                 """

    #                 cursor.execute(
    #                     insert_query,
    #                     (masala_id, cust_name, masala_name, qty, rate, amount)
    #                 )

    #                 inserted = True

    #         if not error_found:
    #             connection.commit()

    #         if inserted:
    #             st.success("Order Inserted Successfully")
    #         else:
    #             st.error("Please enter valid Qty and Rate")


    # ================= UPDATE PAGE =================
    elif menu == "Update":

        st.title("Update Masala Order")

        cust_name = st.selectbox("Select Customer", cust_df["shop_name"])

        # cust_name = st.text_input("Customer Name")
        masala_name = st.selectbox("Masala Name", df["masala_name"])

        col1, col2 = st.columns(2)

        new_qty = col1.number_input("New Quantity", min_value=1)
        new_rate = col2.number_input("New Rate", min_value=1)

        if st.button("Update Order"):

            new_amount = new_qty * new_rate

            cursor = connection.cursor()

            update_query = """
            UPDATE masala_order
            SET qty = %s,
                rate = %s,
                amount = %s
            WHERE cust_name = %s
            AND masala_name = %s
            AND business_date = CURRENT_DATE
            """

            cursor.execute(update_query,
                           (new_qty, new_rate, new_amount, cust_name, masala_name))

            connection.commit()

            st.success("Order Updated Successfully")


# ******************************delivery****************


    elif menu == "Delivery":

        # ---------------- PAGE TITLE ----------------
        st.subheader("🚚 Delivery Update")

        # ---------------- FETCH PENDING CUSTOMERS ----------------
        pending_cust_query = """
            SELECT DISTINCT cust_name
            FROM masala_order
            WHERE status = 'Pending'
            ORDER BY cust_name
        """

        pending_df = pd.read_sql(pending_cust_query, connection)

        # ---------------- NO DATA CASE ----------------
        if pending_df.empty:
            st.warning("No pending customers found")
            st.stop()

        # ---------------- CUSTOMER SELECTION ----------------
        cust_name = st.selectbox(
            "Select Customer",
            pending_df["cust_name"],
            index=0
        )

        # ---------------- FETCH CUSTOMER ITEMS ----------------
        items_query = """
            SELECT seq, masala_name, qty, rate
            FROM masala_order
            WHERE status = 'Pending'
            AND cust_name = %s
            ORDER BY seq
        """

        items_df = pd.read_sql(items_query, connection, params=(cust_name,))

        # ---------------- NO ITEMS ----------------
        if items_df.empty:
            st.warning("No pending items for selected customer")
            st.stop()

        st.markdown("### 📦 Order Details")

        # ---------------- HEADER ROW ----------------
        h1, h2, h3, h4 = st.columns([3, 1.5, 1.5, 2])
        h1.markdown("**Masala Name**")
        h2.markdown("**Ordered Qty**")
        h3.markdown("**Rate**")
        h4.markdown("**Delivered Qty**")

        # ---------------- STORE DATA ----------------
        delivery_data = []

        # ---------------- LOOP ITEMS ----------------
        for _, row in items_df.iterrows():

            seq = int(row["seq"])
            masala_name = row["masala_name"]
            ordered_qty = int(row["qty"])
            rate = float(row["rate"])

            col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 2])

            col1.write(masala_name)
            col2.write(ordered_qty)
            col3.write(f"₹ {rate:.2f}")

            # delivered_qty = col4.number_input(
            #     label="",
            #     min_value=0,
            #     max_value=ordered_qty,
            #     value=ordered_qty,
            #     step=1,
            #     key=f"del_qty_{seq}"
            # )

            delivered_qty = col4.number_input(
    "Delivered Qty",
    min_value=0,
    max_value=ordered_qty,
    value=ordered_qty,
    step=1,
    key=f"del_qty_{seq}",
    label_visibility="collapsed"
)

            delivery_data.append({
                "seq": seq,
                "name": masala_name,
                "ordered": ordered_qty,
                "delivered": delivered_qty,
                "rate": rate
            })

        # ---------------- BUTTONS ----------------
        st.markdown("---")
        btn1, btn2 = st.columns(2)

        # ================= UPDATE DELIVERY =================
        with btn1:
            if st.button("✅ Update Delivery", use_container_width=True):

                cursor = connection.cursor()

                for item in delivery_data:

                    seq = item["seq"]
                    masala_name = item["name"]
                    ordered_qty = item["ordered"]
                    delivered_qty = item["delivered"]
                    rate = item["rate"]

                    # -------- VALIDATION --------
                    if delivered_qty < 0:
                        st.error(f"{masala_name}: Invalid quantity")
                        continue

                    if delivered_qty > ordered_qty:
                        st.error(f"{masala_name}: Delivered > Ordered not allowed")
                        continue

                    # -------- STATUS LOGIC --------
                    if delivered_qty == ordered_qty:
                        status = "Delivered"
                    elif delivered_qty == 0:
                        status = "Pending"
                    else:
                        status = "Partial"

                    amount_del = delivered_qty * rate

                    # -------- UPDATE QUERY --------
                    cursor.execute("""
                        UPDATE masala_order
                        SET qty_del = %s,
                            amount_del = %s,
                            business_date_del = CURRENT_DATE,
                            order_time_del = CURRENT_TIMESTAMP,
                            status = %s
                        WHERE seq = %s
                    """, (
                        delivered_qty,
                        amount_del,
                        status,
                        seq
                    ))

                connection.commit()
                cursor.close()

                st.success(f"Delivery updated successfully for {cust_name} ✅")

                                # ===== FETCH UPDATED DATA FROM DB =====

                bill_query = """
                    SELECT
                        masala_name,
                        qty_del,
                        rate
                    FROM masala_order
                    WHERE cust_name = %s
                    AND status IN ('Delivered','Partial')
                    AND business_date_del = CURRENT_DATE
                """
                
                bill_df = pd.read_sql(
                    bill_query,
                    connection,
                    params=(cust_name,)
                )
                
                if bill_df.empty:
                
                    st.warning("No delivered items found for billing")
                
                    st.stop()
                
                # =====================================================
                # ================= PREPARE TABLE DATA =================
                # =====================================================
                
                total = 0
                
                table_data = [[
                    "Masala Name",
                    "Quantity",
                    "Rate",
                    "Amount"
                ]]
                
                for _, row in bill_df.iterrows():
                
                    amount = row["qty_del"] * row["rate"]
                
                    total += amount
                
                    table_data.append([
                        row["masala_name"],
                        int(row["qty_del"]),
                        f"₹ {row['rate']:.2f}",
                        f"₹ {amount:.2f}"
                    ])
                
                # ===== TOTAL ROW =====
                
                table_data.append([
                    "",
                    "",
                    "TOTAL",
                    f"₹ {total:.2f}"
                ])
                
                # =====================================================
                # ================= GENERATE PDF ======================
                # =====================================================
                
                from io import BytesIO
                
                from reportlab.platypus import (
                    SimpleDocTemplate,
                    Table,
                    TableStyle,
                    Paragraph,
                    Spacer
                )
                
                from reportlab.lib import colors
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.units import inch
                
                buffer = BytesIO()
                
                # =====================================================
                # ================= PDF DOCUMENT ======================
                # =====================================================
                
                doc = SimpleDocTemplate(
                    buffer,
                    pagesize=A4,
                    rightMargin=30,
                    leftMargin=30,
                    topMargin=30,
                    bottomMargin=20
                )
                
                elements = []
                
                styles = getSampleStyleSheet()
                
                # =====================================================
                # ================= TITLE =============================
                # =====================================================
                
                title = Paragraph(
                    "<font size=20><b>MASALA DELIVERY BILL</b></font>",
                    styles['Title']
                )
                
                elements.append(title)
                
                elements.append(Spacer(1, 20))
                
                # =====================================================
                # ================= CUSTOMER INFO =====================
                # =====================================================
                
                customer_info = f"""
                <font size=12>
                <b>Customer:</b> {cust_name}<br/>
                <b>Date:</b> {datetime.now().strftime('%d-%m-%Y %H:%M')}
                </font>
                """
                
                elements.append(
                    Paragraph(
                        customer_info,
                        styles['Normal']
                    )
                )
                
                elements.append(Spacer(1, 20))
                
                # =====================================================
                # ================= FULL WIDTH TABLE ==================
                # =====================================================
                
                table = Table(
                
                    table_data,
                
                    colWidths=[
                    
                        3.5 * inch,
                        1.2 * inch,
                        1.2 * inch,
                        1.5 * inch
                    ]
                )
                
                # =====================================================
                # ================= TABLE STYLE =======================
                # =====================================================
                
                table.setStyle(TableStyle([
                
                    # ===== HEADER =====
                
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                
                    ('FONTSIZE', (0, 0), (-1, 0), 13),
                
                    # ===== BODY =====
                
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                
                    ('FONTSIZE', (0, 1), (-1, -1), 11),
                
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                
                    # ===== TOTAL ROW =====
                
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                
                    # ===== GRID =====
                
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                
                    # ===== PADDING =====
                
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                
                    # ===== ROW BACKGROUND =====
                
                    ('BACKGROUND', (0, 1), (-1, -2), colors.whitesmoke),
                
                ]))
                
                elements.append(table)
                
                elements.append(Spacer(1, 30))
                
                # =====================================================
                # ================= FOOTER ============================
                # =====================================================
                
                footer = Paragraph(
                    "<font size=11><b>Thank You Visit Again</b></font>",
                    styles['Normal']
                )
                
                elements.append(footer)
                
                # =====================================================
                # ================= BUILD PDF =========================
                # =====================================================
                
                doc.build(elements)
                
                buffer.seek(0)
                
                # =====================================================
                # ================= DOWNLOAD BUTTON ===================
                # =====================================================
                
                st.download_button(
                    label="📄 Download Bill PDF",
                    data=buffer,
                    file_name=f"{cust_name}_bill.pdf",
                    mime="application/pdf"
                )


                # bill_query = """
                #     SELECT masala_name, qty_del, rate
                #     FROM masala_order
                #     WHERE cust_name = %s
                #     AND status IN ('Delivered','Partial')
                #     AND business_date_del = CURRENT_DATE
                # """
                # bill_df = pd.read_sql(bill_query, connection, params=(cust_name,))

                # if bill_df.empty:
                #     st.warning("No delivered items found for billing")
                #     st.stop()

                # # ===== PREPARE DATA =====
                # total = 0
                # table_data = [["Masala", "Qty", "Rate", "Amount"]]

                # for _, row in bill_df.iterrows():
                #     amount = row["qty_del"] * row["rate"]
                #     total += amount

                #     table_data.append([
                #         row["masala_name"],
                #         int(row["qty_del"]),
                #         f"₹ {row['rate']:.2f}",
                #         f"₹ {amount:.2f}"
                #     ])

                # table_data.append(["", "", "Total", f"₹ {total:.2f}"])

                # # ===== GENERATE PDF =====
                # from io import BytesIO
                # from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                # from reportlab.lib import colors
                # from reportlab.lib.styles import getSampleStyleSheet
                

                # buffer = BytesIO()
                # doc = SimpleDocTemplate(buffer)
                # elements = []
                # styles = getSampleStyleSheet()

                # # Title
                # elements.append(Paragraph("🧾 MASALA DELIVERY BILL", styles['Title']))
                # elements.append(Spacer(1, 10))

                # # Customer info
                # elements.append(Paragraph(f"Customer: {cust_name}", styles['Normal']))
                # elements.append(Paragraph(f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}", styles['Normal']))
                # elements.append(Spacer(1, 10))

                # # Table
                # table = Table(table_data)

                # table.setStyle(TableStyle([
                #     ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                #     ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                #     ("GRID", (0, 0), (-1, -1), 1, colors.black),
                #     ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                # ]))

                # elements.append(table)

                # doc.build(elements)
                # buffer.seek(0)

                # # ===== DOWNLOAD BUTTON =====
                # st.download_button(
                #     label="📄 Download Bill PDF",
                #     data=buffer,
                #     file_name=f"{cust_name}_bill.pdf",
                #     mime="application/pdf"
                # )

        # ================= CANCEL ORDER =================
        with btn2:

            confirm_cancel = st.checkbox("Confirm Cancel Order")

            if st.button("❌ Cancel Order", use_container_width=True):

                if not confirm_cancel:
                    st.warning("Please confirm cancellation first")
                    st.stop()

                cursor = connection.cursor()

                cursor.execute("""
                    UPDATE masala_order
                    SET status = 'Cancelled',
                        qty_del = 0,
                        amount_del = 0,
                        business_date_del = CURRENT_DATE,
                        order_time_del = CURRENT_TIMESTAMP
                    WHERE cust_name = %s
                    AND status = 'Pending'
                """, (cust_name,))

                connection.commit()
                cursor.close()

                st.error(f"Order cancelled for {cust_name} ❌")

       
       
       # ================= BILL PAGE =================

    elif menu == "Bill":

        st.subheader("🧾 Generate Customer Bill")

        # ================= BILL TYPE =================

        bill_type = st.radio(
            "Select Bill Type",
            ["Delivered", "Pending"],
            horizontal=True
        )

        # =========================================================
        # ================= DELIVERED BILL ========================
        # =========================================================

        if bill_type == "Delivered":

            # -------- FETCH CUSTOMERS --------

            bill_cust_query = """
                SELECT DISTINCT cust_name
                FROM masala_order
                WHERE status IN ('Delivered','Partial')
                ORDER BY cust_name
            """

            bill_cust_df = pd.read_sql(
                bill_cust_query,
                connection
            )

            if bill_cust_df.empty:
                st.warning("No delivered customers found")
                st.stop()

            # -------- SELECT BOXES --------

            col1, col2 = st.columns(2)

            with col1:

                cust_name = st.selectbox(
                    "Select Customer",
                    bill_cust_df["cust_name"],
                    key="del_customer"
                )

            # -------- FETCH DELIVERY DATES --------

            date_query = """
                SELECT DISTINCT business_date_del
                FROM masala_order
                WHERE cust_name = %s
                AND status IN ('Delivered','Partial')
                ORDER BY business_date_del DESC
            """

            date_df = pd.read_sql(
                date_query,
                connection,
                params=(cust_name,)
            )

            if date_df.empty:
                st.warning("No delivery dates found")
                st.stop()

            with col2:

                selected_date = st.selectbox(
                    "Select Delivery Date",
                    date_df["business_date_del"],
                    key="del_date"
                )

            # -------- FETCH BILL DATA --------

            bill_query = """
                SELECT
                    masala_name,
                    qty_del,
                    rate
                FROM masala_order
                WHERE cust_name = %s
                AND status IN ('Delivered','Partial')
                AND business_date_del = %s
            """

            bill_df = pd.read_sql(
                bill_query,
                connection,
                params=(cust_name, selected_date)
            )

            if bill_df.empty:
                st.warning("No delivered items found")
                st.stop()

            st.markdown("### 📦 Delivered Items")

            # -------- DISPLAY TABLE --------

            total = 0
            display_data = []

            for _, row in bill_df.iterrows():

                amount = row["qty_del"] * row["rate"]

                total += amount

                display_data.append({
                    "Masala": row["masala_name"],
                    "Qty": int(row["qty_del"]),
                    "Rate": f"₹ {row['rate']:.2f}",
                    "Amount": f"₹ {amount:.2f}"
                })

            st.dataframe(
                display_data,
                use_container_width=True
            )

            st.markdown(f"### 💰 Total: ₹ {total:.2f}")


                        # -------- GENERATE PDF --------

            if st.button("📄 Generate & Download Delivered Bill"):

                from reportlab.platypus import (
                    SimpleDocTemplate,
                    Table,
                    TableStyle,
                    Paragraph,
                    Spacer
                )

                from reportlab.lib import colors
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.units import inch
                from io import BytesIO

                buffer = BytesIO()

                # =====================================================
                # ================= PDF DOCUMENT ======================
                # =====================================================

                doc = SimpleDocTemplate(
                    buffer,
                    pagesize=A4,
                    rightMargin=30,
                    leftMargin=30,
                    topMargin=30,
                    bottomMargin=20
                )

                elements = []

                styles = getSampleStyleSheet()

                # =====================================================
                # ================= TITLE =============================
                # =====================================================

                title = Paragraph(
                    "<font size=20><b>MASALA DELIVERY BILL</b></font>",
                    styles['Title']
                )

                elements.append(title)

                elements.append(Spacer(1, 20))

                # =====================================================
                # ================= CUSTOMER INFO =====================
                # =====================================================

                customer_info = f"""
                <font size=12>
                <b>Customer:</b> {cust_name}<br/>
                <b>Delivery Date:</b> {selected_date}
                </font>
                """

                elements.append(
                    Paragraph(customer_info, styles['Normal'])
                )

                elements.append(Spacer(1, 20))

                # =====================================================
                # ================= TABLE DATA ========================
                # =====================================================

                table_data = []

                # Header Row
                table_data.append([
                    "Masala Name",
                    "Quantity",
                    "Rate",
                    "Amount"
                ])

                # Data Rows
                for row in display_data:
                
                    table_data.append([
                        row["Masala"],
                        str(row["Qty"]),
                        row["Rate"],
                        row["Amount"]
                    ])

                # Total Row
                table_data.append([
                    "",
                    "",
                    "TOTAL",
                    f"₹ {total:.2f}"
                ])

                # =====================================================
                # ================= FULL PAGE TABLE ===================
                # =====================================================

                table = Table(
                    table_data,

                    # Full Width Columns
                    colWidths=[
                        3.5 * inch,
                        1.2 * inch,
                        1.2 * inch,
                        1.5 * inch
                    ]
                )

                # =====================================================
                # ================= TABLE STYLE =======================
                # =====================================================

                table.setStyle(TableStyle([
                
                    # Header Background
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),

                    # Header Text Color
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

                    # Header Font
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

                    # Header Font Size
                    ('FONTSIZE', (0, 0), (-1, 0), 13),

                    # Body Font
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),

                    # Body Font Size
                    ('FONTSIZE', (0, 1), (-1, -1), 11),

                    # Alignment
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),

                    # Total Row Bold
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),

                    # Total Row Background
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),

                    # Grid
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),

                    # Padding
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),

                    # Alternate Row Background
                    ('BACKGROUND', (0, 1), (-1, -2), colors.whitesmoke),

                ]))

                elements.append(table)

                elements.append(Spacer(1, 30))

                # =====================================================
                # ================= FOOTER ============================
                # =====================================================

                footer = Paragraph(
                    "<font size=11><b>Thank You Visit Again</b></font>",
                    styles['Normal']
                )

                elements.append(footer)

                # =====================================================
                # ================= BUILD PDF =========================
                # =====================================================

                doc.build(elements)

                buffer.seek(0)

                # =====================================================
                # ================= DOWNLOAD BUTTON ===================
                # =====================================================

                st.download_button(
                    label="⬇ Download Delivered PDF",
                    data=buffer,
                    file_name=f"{cust_name}_{selected_date}_delivered_bill.pdf",
                    mime="application/pdf"
                )

        # =========================================================
        # ================= PENDING BILL ==========================
        # =========================================================

        elif bill_type == "Pending":

            # -------- FETCH CUSTOMERS --------

            pending_cust_query = """
                SELECT DISTINCT cust_name
                FROM masala_order
                WHERE status = 'Pending'
                ORDER BY cust_name
            """

            pending_cust_df = pd.read_sql(
                pending_cust_query,
                connection
            )

            if pending_cust_df.empty:
                st.warning("No pending customers found")
                st.stop()

            # -------- SELECT BOXES --------

            col1, col2 = st.columns(2)

            with col1:

                cust_name = st.selectbox(
                    "Select Pending Customer",
                    pending_cust_df["cust_name"],
                    key="pending_customer"
                )

            # -------- FETCH PENDING DATES --------

            pending_date_query = """
                SELECT DISTINCT business_date
                FROM masala_order
                WHERE cust_name = %s
                AND status = 'Pending'
                ORDER BY business_date DESC
            """

            pending_date_df = pd.read_sql(
                pending_date_query,
                connection,
                params=(cust_name,)
            )

            if pending_date_df.empty:
                st.warning("No pending dates found")
                st.stop()

            with col2:

                selected_pending_date = st.selectbox(
                    "Select Pending Date",
                    pending_date_df["business_date"],
                    key="pending_date"
                )

            # -------- FETCH PENDING ITEMS --------

            pending_bill_query = """
                SELECT
                    masala_name,
                    qty,
                    rate
                FROM masala_order
                WHERE cust_name = %s
                AND status = 'Pending'
                AND business_date = %s
            """

            pending_bill_df = pd.read_sql(
                pending_bill_query,
                connection,
                params=(
                    cust_name,
                    selected_pending_date
                )
            )

            if pending_bill_df.empty:
                st.warning("No pending items found")
                st.stop()

            st.markdown("### 📦 Pending Items")

            # -------- DISPLAY TABLE --------

            pending_total = 0

            pending_display_data = []

            for _, row in pending_bill_df.iterrows():

                amount = row["qty"] * row["rate"]

                pending_total += amount

                pending_display_data.append({

                    "Masala": row["masala_name"],

                    "Qty": int(row["qty"]),

                    "Rate": f"₹ {row['rate']:.2f}",

                    "Amount": f"₹ {amount:.2f}"
                })

            st.dataframe(
                pending_display_data,
                use_container_width=True
            )

            st.markdown(
                f"### 💰 Pending Total: ₹ {pending_total:.2f}"
            )

            # -------- GENERATE PDF --------

            if st.button("📄 Generate & Download Pending Bill"):
            
                from reportlab.platypus import (
                    SimpleDocTemplate,
                    Table,
                    TableStyle,
                    Paragraph,
                    Spacer
                )
        
                from reportlab.lib import colors
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.units import inch
                from io import BytesIO
        
                buffer = BytesIO()
        
                # ===== A4 PAGE WITH MARGINS =====
        
                doc = SimpleDocTemplate(
                    buffer,
                    pagesize=A4,
                    rightMargin=30,
                    leftMargin=30,
                    topMargin=30,
                    bottomMargin=20
                )
        
                elements = []
        
                styles = getSampleStyleSheet()
        
                # =====================================================
                # ================= TITLE =============================
                # =====================================================
        
                title = Paragraph(
                    "<font size=20><b>MASALA PENDING BILL</b></font>",
                    styles['Title']
                )
        
                elements.append(title)
        
                elements.append(Spacer(1, 20))
        
                # =====================================================
                # ================= CUSTOMER INFO =====================
                # =====================================================
        
                customer_info = f"""
                <font size=12>
                <b>Customer:</b> {cust_name}<br/>
                <b>Pending Date:</b> {selected_pending_date}
                </font>
                """
        
                elements.append(
                    Paragraph(customer_info, styles['Normal'])
                )
        
                elements.append(Spacer(1, 20))
        
                # =====================================================
                # ================= TABLE DATA ========================
                # =====================================================
        
                table_data = []
        
                # Header
                table_data.append([
                    "Masala Name",
                    "Quantity",
                    "Rate",
                    "Amount"
                ])
        
                # Data Rows
                for row in pending_display_data:
                
                    table_data.append([
                        row["Masala"],
                        str(row["Qty"]),
                        row["Rate"],
                        row["Amount"]
                    ])
        
                # Total Row
                table_data.append([
                    "",
                    "",
                    "TOTAL",
                    f"₹ {pending_total:.2f}"
                ])
        
                # =====================================================
                # ================= FULL WIDTH TABLE ==================
                # =====================================================
        
                table = Table(
                    table_data,
        
                    # Full Page Width
                    colWidths=[
                        3.5 * inch,
                        1.2 * inch,
                        1.2 * inch,
                        1.5 * inch
                    ]
                )
        
                # =====================================================
                # ================= TABLE STYLE =======================
                # =====================================================
        
                table.setStyle(TableStyle([
                
                    # Header Background
                    ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
        
                    # Header Text Color
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        
                    # Header Font
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        
                    # Header Font Size
                    ('FONTSIZE', (0, 0), (-1, 0), 13),
        
                    # Body Font
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        
                    # Body Font Size
                    ('FONTSIZE', (0, 1), (-1, -1), 11),
        
                    # Alignment
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        
                    # Total Row Bold
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        
                    # Total Row Background
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        
                    # Grid
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
                    # Padding
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        
                    # Alternate Row Colors
                    ('BACKGROUND', (0, 1), (-1, -2), colors.whitesmoke),
        
                ]))
        
                elements.append(table)
        
                elements.append(Spacer(1, 30))
        
                # =====================================================
                # ================= FOOTER ============================
                # =====================================================
        
                footer = Paragraph(
                    "<font size=11><b>Your product will be delivered soon</b></font>",
                    styles['Normal']
                )
        
                elements.append(footer)
        
                # =====================================================
                # ================= BUILD PDF =========================
                # =====================================================
        
                doc.build(elements)
        
                buffer.seek(0)
        
                # =====================================================
                # ================= DOWNLOAD BUTTON ===================
                # =====================================================
        
                st.download_button(
                    label="⬇ Download Pending PDF",
                    data=buffer,
                    file_name=f"{cust_name}_{selected_pending_date}_pending_bill.pdf",
                    mime="application/pdf"
                )

            # # -------- GENERATE PDF --------

            # if st.button("📄 Generate & Download Pending Bill"):

            #     from reportlab.platypus import (
            #         SimpleDocTemplate,
            #         Table,
            #         TableStyle,
            #         Paragraph,
            #         Spacer
            #     )

            #     from reportlab.lib import colors
            #     from reportlab.lib.styles import getSampleStyleSheet
            #     from io import BytesIO

            #     buffer = BytesIO()

            #     doc = SimpleDocTemplate(buffer)

            #     elements = []

            #     styles = getSampleStyleSheet()

            #     # ===== TITLE =====

            #     elements.append(
            #         Paragraph(
            #             "MASALA PENDING BILL",
            #             styles['Title']
            #         )
            #     )

            #     elements.append(Spacer(1, 10))

            #     # ===== CUSTOMER =====

            #     elements.append(
            #         Paragraph(
            #             f"Customer: {cust_name}",
            #             styles['Normal']
            #         )
            #     )

            #     elements.append(
            #         Paragraph(
            #             f"Pending Date: {selected_pending_date}",
            #             styles['Normal']
            #         )
            #     )

            #     elements.append(Spacer(1, 10))

            #     # ===== TABLE =====

            #     table_data = [
            #         ["Masala", "Qty", "Rate", "Amount"]
            #     ]

            #     for row in pending_display_data:

            #         table_data.append([
            #             row["Masala"],
            #             row["Qty"],
            #             row["Rate"],
            #             row["Amount"]
            #         ])

            #     table_data.append([
            #         "",
            #         "",
            #         "Total",
            #         f"₹ {pending_total:.2f}"
            #     ])

            #     table = Table(table_data)

            #     table.setStyle(TableStyle([

            #         ("BACKGROUND", (0, 0), (-1, 0), colors.orange),

            #         ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            #         ("GRID", (0, 0), (-1, -1), 1, colors.black),

            #         ("ALIGN", (1, 1), (-1, -1), "CENTER"),

            #         ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            #         ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

            #     ]))

            #     elements.append(table)

            #     doc.build(elements)

            #     buffer.seek(0)

            #     st.download_button(
            #         label="⬇ Download Pending PDF",
            #         data=buffer,
            #         file_name=f"{cust_name}_{selected_pending_date}_pending_bill.pdf",
            #         mime="application/pdf"
            #     )    

       
    #     # ================= BILL PAGE =================
        
    # elif menu == "Bill":

    #     st.subheader("🧾 Generate Customer Bill")

    #     # -------- FETCH CUSTOMERS --------
    #     bill_cust_query = """
    #         SELECT DISTINCT cust_name
    #         FROM masala_order
    #         WHERE status IN ('Delivered','Partial')
    #         ORDER BY cust_name
    #     """
    #     bill_cust_df = pd.read_sql(bill_cust_query, connection)

    #     if bill_cust_df.empty:
    #         st.warning("No delivered customers found")
    #         st.stop()

    #     # -------- SIDE BY SIDE SELECT BOXES --------
    #     col1, col2 = st.columns(2)

    #     with col1:
    #         cust_name = st.selectbox(
    #             "Select Customer",
    #             bill_cust_df["cust_name"]
    #         )

    #     # -------- FETCH DATES BASED ON CUSTOMER --------
    #     date_query = """
    #         SELECT DISTINCT business_date_del
    #         FROM masala_order
    #         WHERE cust_name = %s
    #         AND status IN ('Delivered','Partial')
    #         ORDER BY business_date_del DESC
    #     """
    #     date_df = pd.read_sql(date_query, connection, params=(cust_name,))

    #     if date_df.empty:
    #         st.warning("No delivery dates found for this customer")
    #         st.stop()

    #     with col2:
    #         selected_date = st.selectbox(
    #             "Select Delivery Date",
    #             date_df["business_date_del"]
    #         )

    #     # -------- FETCH BILL DATA --------
    #     bill_query = """
    #         SELECT masala_name, qty_del, rate
    #         FROM masala_order
    #         WHERE cust_name = %s
    #         AND status IN ('Delivered','Partial')
    #         AND business_date_del = %s
    #     """
    #     bill_df = pd.read_sql(bill_query, connection, params=(cust_name, selected_date))

    #     if bill_df.empty:
    #         st.warning("No delivered items found")
    #         st.stop()

    #     st.markdown("### 📦 Delivered Items")

    #     # -------- DISPLAY TABLE --------
    #     total = 0
    #     display_data = []

    #     for _, row in bill_df.iterrows():
    #         amount = row["qty_del"] * row["rate"]
    #         total += amount

    #         display_data.append({
    #             "Masala": row["masala_name"],
    #             "Qty": int(row["qty_del"]),
    #             "Rate": f"₹ {row['rate']:.2f}",
    #             "Amount": f"₹ {amount:.2f}"
    #         })

    #     st.dataframe(display_data, use_container_width=True)
    #     st.markdown(f"### 💰 Total: ₹ {total:.2f}")

    #     # -------- GENERATE PDF --------
    #     if st.button("📄 Generate & Download Bill"):

    #         from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    #         from reportlab.lib import colors
    #         from reportlab.lib.styles import getSampleStyleSheet
    #         from io import BytesIO

    #         buffer = BytesIO()
    #         doc = SimpleDocTemplate(buffer)
    #         elements = []
    #         styles = getSampleStyleSheet()

    #         # Title
    #         elements.append(Paragraph("🧾 MASALA DELIVERY BILL", styles['Title']))
    #         elements.append(Spacer(1, 10))

    #         # Customer + Date
    #         elements.append(Paragraph(f"Customer: {cust_name}", styles['Normal']))
    #         elements.append(Paragraph(f"Delivery Date: {selected_date}", styles['Normal']))
    #         elements.append(Spacer(1, 10))

    #         # Table
    #         table_data = [["Masala", "Qty", "Rate", "Amount"]]

    #         for row in display_data:
    #             table_data.append([
    #                 row["Masala"],
    #                 row["Qty"],
    #                 row["Rate"],
    #                 row["Amount"]
    #             ])

    #         table_data.append(["", "", "Total", f"₹ {total:.2f}"])

    #         table = Table(table_data)

    #         table.setStyle(TableStyle([
    #             ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
    #             ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    #             ("GRID", (0, 0), (-1, -1), 1, colors.black),
    #             ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    #         ]))

    #         elements.append(table)

    #         doc.build(elements)
    #         buffer.seek(0)

    #         st.download_button(
    #             label="⬇ Download PDF",
    #             data=buffer,
    #             file_name=f"{cust_name}_{selected_date}_bill.pdf",
    #             mime="application/pdf"
    #         )
            

    # ================= DELIVERY =================
    # elif menu == "Delivery":

    #     st.subheader("Delivery Update")

    #     # Fetch pending customers
    #     pending_cust_query = """
    #     SELECT DISTINCT cust_name 
    #     FROM masala_order 
    #     WHERE status = 'Pending';
    #     """

    #     pending_df = pd.read_sql(pending_cust_query, connection)

    #     if pending_df.empty:
    #         st.warning("No pending customers")
    #     else:
    #         cust_name = st.selectbox("Select Customer", pending_df["cust_name"])

    #         # Fetch pending items
    #         items_query = """
    #         SELECT seq, masala_name, qty, rate 
    #         FROM masala_order 
    #         WHERE status = 'Pending' 
    #         AND cust_name = %s
    #         """

    #         items_df = pd.read_sql(items_query, connection, params=(cust_name,))

    #         if items_df.empty:
    #             st.warning("No pending items")
    #         else:

    #             st.write("Enter Delivered Quantity:")

    #             delivery_data = []

    #             for _, row in items_df.iterrows():

    #                 seq = row["seq"]
    #                 masala_name = row["masala_name"]
    #                 ordered_qty = row["qty"]
    #                 rate = row["rate"]

    #                 col1, col2, col3 = st.columns([2,1,1])

    #                 col1.write(f"**{masala_name}**")
    #                 col2.write(f"Ordered: {ordered_qty}")

    #                 # ✅ Only Qty input (NO dropdown)
    #                 delivered_qty = col3.number_input(
    #                     "Delivered Qty",
    #                     min_value=0,
    #                     max_value=int(ordered_qty),
    #                     value=int(ordered_qty),
    #                     key=f"qty_{seq}"
    #                 )

    #                 delivery_data.append((seq, masala_name, ordered_qty, delivered_qty, rate))

    #             # ---------------- UPDATE BUTTON ----------------
    #             if st.button("Update Delivery"):

    #                 cursor = connection.cursor()

    #                 for data in delivery_data:

    #                     seq, masala_name, ordered_qty, delivered_qty, rate = data

    #                     # Validation
    #                     if delivered_qty < 0:
    #                         st.error(f"Invalid qty for {masala_name}")
    #                         continue

    #                     if delivered_qty > ordered_qty:
    #                         st.error(f"Delivered qty cannot exceed ordered for {masala_name}")
    #                         continue

    #                     # ✅ Auto Status Logic
    #                     if delivered_qty == ordered_qty:
    #                         status = "Delivered"
    #                     elif delivered_qty == 0:
    #                         status = "Pending"
    #                     else:
    #                         status = "Partial"

    #                     amount_del = delivered_qty * rate

    #                     cursor.execute("""
    #                         UPDATE masala_order
    #                         SET qty_del = %s,
    #                             amount_del = %s,
    #                             business_date_del = CURRENT_DATE,
    #                             order_time_del = CURRENT_TIMESTAMP,
    #                             status = %s
    #                         WHERE seq = %s
    #                     """, (
    #                         delivered_qty,
    #                         amount_del,
    #                         status,
    #                         seq
    #                     ))

    #                 connection.commit()

    #                 st.success(f"Delivery updated for {cust_name} ✅")






























    # # ================= DELIVERY =================
    # elif menu == "Delivery":

    #     st.subheader("Delivery Update")

    #     # Fetch pending customers
    #     pending_cust_query = """
    #     SELECT DISTINCT cust_name 
    #     FROM masala_order 
    #     WHERE status = 'Pending';
    #     """

    #     pending_df = pd.read_sql(pending_cust_query, connection)

    #     if pending_df.empty:
    #         st.warning("No pending customers")
    #     else:
    #         cust_name = st.selectbox("Select Customer", pending_df["cust_name"])

    #         # Fetch items for selected customer
    #         items_query = """
    #         SELECT seq, masala_name, qty, rate, amount, status 
    #         FROM masala_order 
    #         WHERE status = 'Pending' 
    #         AND cust_name = %s
    #         """

    #         items_df = pd.read_sql(items_query, connection, params=(cust_name,))

    #         if items_df.empty:
    #             st.warning("No pending items for this customer")
    #         else:
    #             st.write("Enter Delivered Quantity (Full / Partial):")

    #             # Editable table
    #             edited_df = st.data_editor(
    #                 items_df,
    #                 use_container_width=True,
    #                 num_rows="fixed"
    #             )

    #             # Add delivery qty column if not present
    #             if "qty_del" not in edited_df.columns:
    #                 edited_df["qty_del"] = edited_df["qty"]

    #             # Calculate delivery amount
    #             edited_df["amount_del"] = edited_df["qty_del"] * edited_df["rate"]

    #             st.write("Delivery Preview:", edited_df)

    #             if st.button("Update Delivery"):

    #                 cursor = connection.cursor()

    #                 for _, row in edited_df.iterrows():

    #                     ordered_qty = row["qty"]
    #                     delivered_qty = row["qty_del"]
    #                     rate = row["rate"]
    #                     amount_del = delivered_qty * rate

    #                     # 🔥 Decide status
    #                     if delivered_qty == ordered_qty:
    #                         status = "Delivered"
    #                     elif delivered_qty < ordered_qty:
    #                         status = "Partial"
    #                     else:
    #                         st.error(f"Delivered qty cannot be greater than ordered qty for {row['masala_name']}")
    #                         continue

    #                     # ✅ Update table
    #                     cursor.execute("""
    #                         UPDATE masala_order
    #                         SET qty_del = %s,
    #                             amount_del = %s,
    #                             business_date_del = CURRENT_DATE,
    #                             order_time_del = CURRENT_TIMESTAMP,
    #                             status = %s
    #                         WHERE seq = %s
    #                     """, (
    #                         delivered_qty,
    #                         amount_del,
    #                         status,
    #                         row["seq"]
    #                     ))

    #                 connection.commit()

    #                 st.success(f"Delivery updated for {cust_name} ✅")





    # # # ================= DELIVERY =================
    # elif menu == "Delivery":

    #     st.subheader("Delivery Update")

    #     # Fetch pending customers
    #     pending_cust_query = """
    #     SELECT DISTINCT cust_name 
    #     FROM masala_order 
    #     WHERE status = 'Pending';
    #     """

    #     pending_df = pd.read_sql(pending_cust_query, connection)

    #     if pending_df.empty:
    #         st.warning("No pending customers")
    #     else:
    #         cust_name = st.selectbox("Select Customer", pending_df["cust_name"])

    #         # Fetch items for selected customer
    #         items_query = """
    #         SELECT masala_name, qty, rate, amount, status 
    #         FROM masala_order 
    #         WHERE status = 'Pending' 
    #         AND cust_name = %s
    #         """

    #         items_list_df = pd.read_sql(items_query, connection, params=(cust_name,))

    #         if items_list_df.empty:
    #             st.warning("No pending items for this customer")
    #         else:
    #             st.write("Edit Qty if any damage happened:")

    #             # Editable table
    #             edited_df = st.data_editor(
    #                 items_list_df,
    #                 use_container_width=True
    #             )

    #             # Auto update amount
    #             edited_df["amount"] = edited_df["qty"] * edited_df["rate"]

    #             st.write("Updated Data Preview:", edited_df)

    #             # Update button
    #             if st.button("Update Delivery"):

    #                 cursor = connection.cursor()

    #                 for _, row in edited_df.iterrows():

    #                     cursor.execute("""
    #                         UPDATE masala_order
    #                         SET qty = %s,
    #                             amount = %s,
    #                             status = 'Delivered'
    #                         WHERE cust_name = %s 
    #                         AND masala_name = %s 
    #                         AND status = 'Pending'
    #                     """, (
    #                         row["qty"],
    #                         row["amount"],
    #                         cust_name,
    #                         row["masala_name"]
    #                     ))

    #                 connection.commit()

    #                 st.success(f"Delivery updated for {cust_name} ✅")

    # # # ================= Delivery PAGE =================
    # if menu == "Delivery":

    #     pending_cust = "SELECT distinct cust_name FROM masala_order WHERE status = 'Pending';"
    #     pending_df = pd.read_sql(pending_cust, connection)

    #     cust_name = st.selectbox("Select Customer", pending_df["cust_name"])

    #      # Use selected cust_name dynamically
    #     items_list = f"""
    #                     SELECT masala_name, qty, rate, amount, status 
    #                     FROM masala_order 
    #                     WHERE status = 'Pending' 
    #                     AND cust_name = '{cust_name}'
    #                 """
    #     # items_list = "SELECT masala_name,qty,rate,amount,status FROM masala_order WHERE status = 'Pending'  and cust_name = 'Mauli kirana'"
    #     items_list_df = pd.read_sql(items_list, connection)

    #     st.dataframe(items_list_df)

    #     # ✅ Button to update status
    # # if st.button("Mark as Delivered"):

    # #     cursor = connection.cursor()

    # #     update_query = """
    # #     UPDATE masala_order
    # #     SET status = 'Delivered'
    # #     WHERE cust_name = %s AND status = 'Pending'
    # #     """

    # #     cursor.execute(update_query, (cust_name,))
    # #     connection.commit()

    # #     st.success(f"All items for {cust_name} marked as Delivered ✅")
    



# order_details()


