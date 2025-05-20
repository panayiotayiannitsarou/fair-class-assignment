
# main.py – Πλήρης Streamlit εφαρμογή κατανομής μαθητών με Tabs και κατανομή

import streamlit as st
import pandas as pd
import base64
from io import BytesIO

# --- Ασφάλεια ---
SECURITY_CODE = "katanomi2025"
if 'access_granted' not in st.session_state:
    st.session_state['access_granted'] = False

if not st.session_state['access_granted']:
    code_input = st.text_input("🔒 Εισάγετε Κωδικό Πρόσβασης:", type="password")
    if code_input == SECURITY_CODE:
        st.session_state['access_granted'] = True
        st.experimental_rerun()
    else:
        st.stop()

# --- Tabs ---
intro_tab, contact_tab, distribution_tab, faq_tab = st.tabs([
    "📖 Εισαγωγή & Έμπνευση", "✉️ Επικοινωνία", "🏫 Κατανομή Μαθητών", "💡 Συχνές Ερωτήσεις"])

with intro_tab:
    st.markdown("""
    ### 🎯 Σκοπός της Εφαρμογής
    Η εφαρμογή δημιουργήθηκε για να στηρίξει τη δίκαιη και παιδαγωγικά ισορροπημένη κατανομή των μαθητών της Α’ Δημοτικού.

    Όπως γράφει ο John Donne, «Κανένας άνθρωπος δεν είναι νησί» — και το ίδιο ισχύει για κάθε παιδί στην τάξη. Μια άδικη κατανομή μπορεί να διαταράξει τη συνοχή μιας ομάδας και να επηρεάσει βαθιά την ψυχολογία του κάθε μαθητή.
    
    Το εργαλείο αυτό προσφέρει μια παιδαγωγικά τεκμηριωμένη διαδικασία κατανομής, που λαμβάνει υπόψη φίλους, ιδιαιτερότητες, φύλο, παιδιά εκπαιδευτικών και πολλά άλλα.
    """)

with contact_tab:
    st.markdown("""
    📧 **Email επικοινωνίας:** yiannitsaroupanayiota.katanomi@gmail.com
    """)
    if st.button("📋 Αντιγραφή email"):
        st.code("yiannitsaroupanayiota.katanomi@gmail.com", language="text")

with distribution_tab:
    subtab1, subtab2, subtab3 = st.tabs(["📝 Καταχώριση Μαθητών", "📊 Στατιστικά Τμημάτων", "📋 Αποτελέσματα"])

    with subtab1:
        uploaded_file = st.file_uploader("⬆️ Μεταφορτώστε το αρχείο Excel με τους μαθητές", type=["xlsx"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            st.session_state['students_df'] = df
            st.success("✅ Το αρχείο ανέβηκε επιτυχώς.")
            st.dataframe(df)

    with subtab2:
        if 'classes' in st.session_state:
            stats = []
            for i, cl in enumerate(st.session_state['classes']):
                genders = [s['gender'] for s in cl]
                stats.append({
                    "Τμήμα": f"Τμήμα {i+1}",
                    "Μαθητές": len(cl),
                    "Αγόρια": genders.count('Α'),
                    "Κορίτσια": genders.count('Κ')
                })
            st.dataframe(pd.DataFrame(stats))

    with subtab3:
        if 'classes' in st.session_state:
            for i, cl in enumerate(st.session_state['classes']):
                st.markdown(f"### Τμήμα {i+1}")
                st.table(pd.DataFrame(cl))

            def to_excel(classes):
                output = BytesIO()
                writer = pd.ExcelWriter(output, engine='openpyxl')
                for i, cl in enumerate(classes):
                    df = pd.DataFrame(cl)
                    df.to_excel(writer, index=False, sheet_name=f"Τμήμα {i+1}")
                writer.close()
                return output.getvalue()

            excel_data = to_excel(st.session_state['classes'])
            b64 = base64.b64encode(excel_data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="Κατανομή.xlsx">📥 Κατεβάστε την Κατανομή</a>'
            st.markdown(href, unsafe_allow_html=True)

        elif 'students_df' in st.session_state:
            from app_v3_final_v7 import assign_teacher_children, assign_friends_of_teacher_children, \
                assign_lively_students, assign_special_needs_students, assign_language_needs_students, \
                assign_remaining_students_with_friends, assign_remaining_students_without_friends

            df = st.session_state['students_df']
            students = df.fillna('').to_dict(orient='records')
            for s in students:
                s['id'] = str(s.get('Όνομα', ''))
                s['gender'] = s.get('Φύλο', 'Α')
                s['is_teacher_child'] = s.get('Παιδί Εκπαιδευτικού', '') == 'Ναι'
                s['is_lively'] = s.get('Ζωηρός', '') == 'Ναι'
                s['is_special'] = s.get('Ιδιαιτερότητα', '') == 'Ναι'
                s['is_language_support'] = s.get('Καλή γνώση Ελληνικών', '') == 'Όχι'
                s['friends'] = str(s.get('Φίλος/Φίλη', '')).split(',')
                s['conflicts'] = str(s.get('Συγκρούσεις', '')).split(',')

            num_classes = max(2, len(students) // 25 + (1 if len(students) % 25 else 0))
            classes = [[] for _ in range(num_classes)]

            assign_teacher_children(students, classes)
            assign_friends_of_teacher_children(students, classes)
            assign_lively_students(students, classes)
            assign_special_needs_students(students, classes)
            assign_language_needs_students(students, classes)
            assign_remaining_students_with_friends(students, classes)
            assign_remaining_students_without_friends(students, classes)

            st.session_state['classes'] = classes
            st.experimental_rerun()

with faq_tab:
    st.markdown("""
    ### 💡 Συχνές Ερωτήσεις
    
    **1. Τι κάνει η εφαρμογή;**  
    Κατανέμει τους μαθητές σε τμήματα με βάση παιδαγωγικά και κοινωνικά κριτήρια.

    **2. Πώς εισάγω δεδομένα;**  
    Με μεταφόρτωση αρχείου Excel που περιλαμβάνει τα απαραίτητα πεδία.

    **3. Λαμβάνονται υπόψη οι φίλοι;**  
    Ναι, μόνο όταν οι φιλίες είναι πλήρως αμοιβαίες και δεν δημιουργούν ανισορροπίες.

    **4. Πώς εξάγονται τα αποτελέσματα;**  
    Παρέχεται κουμπί λήψης της τελικής κατανομής σε Excel.
    """)
