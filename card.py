import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from PIL import Image
import psycopg2
import easyocr
import cv2
import os
import matplotlib.pyplot as plt
import re

#EasyOCR 
reader = easyocr.Reader(['ch_sim','en'])

#streamlit page background setup
page_bg_img='''
<style>
[data-testid="stAppViewContainer"]{
        background-color:#2BC69C;   
}
</style>'''
st.set_page_config(page_title= "Business Card Data Extraction with OCR",
                layout= "wide",
                initial_sidebar_state= "expanded",)
st.markdown("<h1 style='text-align: center; color: Black;'>Business Card Data Extraction</h1>", unsafe_allow_html=True)
st.markdown(page_bg_img,unsafe_allow_html=True)
st.divider()

SELECT = option_menu(
        menu_title = None,
        options = ["Upload Image","Migrate to Database","Make Changes","Deletion"],
        icons =["house","hospital","cash","bar-chart"],
        default_index=2,
        orientation="horizontal",
        styles={"container": {"padding": "0!important", "background-color": "white","size":"cover", "width": "100%"},
                "icon": {"color": "black", "font-size": "20px"},
                "nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px", "--hover-color": "#06857D"},
                "nav-link-selected": {"background-color": "#06857D"}})

# CONNECTING WITH MYSQL DATABASE
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="risehigh07",
    database= "bizcardx_data"
                )
mycursor = mydb.cursor()

query='''CREATE TABLE IF NOT EXISTS card_data
                (ID INTEGER PRIMARY KEY AUTO_INCREMENT,
                    Company_Name TEXT,
                    Card_Holder_Name TEXT,
                    Designation TEXT,
                    Phone_Number VARCHAR(50),
                    Email TEXT,
                    Website TEXT,
                    Area TEXT,
                    City TEXT,
                    State TEXT,
                    Pincode VARCHAR(10),
                    Image BLOB
                    )'''
mycursor.execute(query)
mydb.commit()

if SELECT=="Upload Image":
    image_files = st.file_uploader("**Upload the Business Card below:** Image", type=["png","jpg","jpeg"])
	
    if image_files is not None:
        def save_card(image_files):
            with open(os.path.join("cards",image_files.name), "wb") as f:
                f.write(image_files.getbuffer())   
        save_card(image_files)
        
        def image_preview(image,res): 
            for (bbox, text, prob) in res:
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))
                cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                cv2.putText(image, text, (tl[0], tl[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            plt.rcParams['figure.figsize'] = (15,15)
            plt.axis('off')
            plt.imshow(image)
        
        # DISPLAYING THE UPLOADED CARD
        col1,col2 = st.columns(2,gap="large")
        with col1:
            st.markdown("#     ")
            st.markdown("#     ")
            st.markdown("### You have uploaded the card")
            st.image(Image.open(image_files),width=250)

        # DISPLAYING THE CARD WITH HIGHLIGHTS
        with col2:
            st.markdown("#     ")
            st.markdown("#     ")
            with st.spinner("**Please wait processing image...**"):
                st.set_option('deprecation.showPyplotGlobalUse', False)
                saved_img = os.getcwd()+ "\\" + "cards"+ "\\"+ image_files.name
                image = cv2.imread(saved_img)
                res = reader.readtext(saved_img)
                st.markdown("### Image Processed and Data Extracted")
                st.pyplot(image_preview(image,res))
        
        #easy OCR
        saved_img = os.getcwd()+ "\\" + "cards"+ "\\"+ image_files.name
        result = reader.readtext(saved_img,detail = 0,paragraph=False)

        # CONVERTING IMAGE TO BINARY TO UPLOAD TO SQL DATABASE
        def img_to_binary(file):
            # Convert image data to binary format
            with open(file, 'rb') as file:
                binaryData = file.read()
            return binaryData
        
        data = {"Company_Name" : [],
                "Card_Holder_Name" : [],
                "Designation" : [],
                "Phone_Number" :[],
                "Email" : [],
                "Website":[],
                "Area":[],
                "City":[],
                "State":[],
                "Pincode":[],
                "image" : img_to_binary(saved_img)
        }
        
        def get_data(res):
            for ind,i in enumerate(res):

                # To get WEBSITE_URL
                if "www " in i.lower() or "www." in i.lower():
                    data["website"].append(i)
                elif "WWW" in i:
                    data["website"] = res[4] +"." + res[5]

                # To get EMAIL ID
                elif "@" in i:
                    data["email"].append(i)

                # To get MOBILE NUMBER
                elif "-" in i:
                    data["mobile_number"].append(i)
                    if len(data["mobile_number"]) ==2:
                        data["mobile_number"] = " & ".join(data["mobile_number"])

                # To get COMPANY NAME  
                elif ind == len(res)-1:
                    data["company_name"].append(i)

                # To get CARD HOLDER NAME
                elif ind == 0:
                    data["card_holder"].append(i)

                # To get DESIGNATION
                elif ind == 1:
                    data["designation"].append(i)

                # To get AREA
                if re.findall('^[0-9].+, [a-zA-Z]+',i):
                    data["area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+',i):
                    data["area"].append(i)

                # To get CITY NAME
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*',i)
                if match1:
                    data["city"].append(match1[0])
                elif match2:
                    data["city"].append(match2[0])
                elif match3:
                    data["city"].append(match3[0])

                # To get STATE
                state_match = re.findall('[a-zA-Z]{9} +[0-9]',i)
                if state_match:
                    data["state"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);',i):
                    data["state"].append(i.split()[-1])
                if len(data["state"])== 2:
                    data["state"].pop(0)

                # To get PINCODE        
                if len(i)>=6 and i.isdigit():
                    data["pin_code"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]',i):
                    data["pin_code"].append(i[10:])
        get_data(result)
    st.button("Store Data", key='switch_button')


if SELECT=="Migrate to Database":
    st.subheader("Database")
    #FUNCTION TO CREATE DATAFRAME
    def create_df(data):
            df = pd.DataFrame(data)
            return df
    df = create_df(data)
    st.success("### Data Extracted!")
    st.write(df)
        
    if st.button("Upload to Database"):
        for i,row in df.iterrows():
            sql = """INSERT INTO card_data(select Company_Name,
                        Card_Holder_Name,
                    Designation,
                    Phone_Number,
                    Email,
                    Website,
                    Area,
                    City,
                    State,
                    Pincode,
                    image)
                    
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            mycursor.execute(sql, tuple(row))
            mydb.commit()
            st.success("#### Uploaded to database successfully!")
    
    if st.button("View updated data"):
        mycursor.execute('''select Company_Name,
                        Card_Holder_Name,
                    Designation,
                    Phone_Number,
                    Email,
                    Website,
                    Area,
                    City,
                    State,
                    Pincode from card_data''')
        updated_df = pd.DataFrame(mycursor.fetchall(),columns=["Company_Name",
                    "Card_Holder_Name",
                    "Designation",
                    "Phone_Number",
                    "Email",
                    "Website",
                    "Area",
                    "City",
                    "State",
                    "Pincode"])
        st.write(updated_df)
st.button("Changes", key='switch_button') 

if SELECT=="Make Changes":
    st.subheader("Alterations")
    col1,col2,col3 = st.columns([3,3,2])
    col2.markdown("## Alter or Delete the data here")
    column1,column2 = st.columns(2,gap="large")
    try:
        with column1:
            mycursor.execute("SELECT card_holder FROM card_data")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
            st.markdown("#### Update or modify any data below")
            mycursor.execute("select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data WHERE card_holder=%s",
                            (selected_card,))
            result = mycursor.fetchone()

            # DISPLAYING ALL THE INFORMATIONS
            company_name = st.text_input("Company_Name", result[0])
            card_holder = st.text_input("Card_Holder", result[1])
            designation = st.text_input("Designation", result[2])
            mobile_number = st.text_input("Mobile_Number", result[3])
            email = st.text_input("Email", result[4])
            website = st.text_input("Website", result[5])
            area = st.text_input("Area", result[6])
            city = st.text_input("City", result[7])
            state = st.text_input("State", result[8])
            pin_code = st.text_input("Pin_Code", result[9])
            
            if st.button("View updated data"):
                mycursor.execute("select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data")
                updated_df = pd.DataFrame(mycursor.fetchall(),columns=["Company_Name","Card_Holder","Designation","Mobile_Number","Email","Website","Area","City","State","Pin_Code"])
                st.write(updated_df)

            elif st.button("Commit changes to DB"):
                # Update the information for the selected business card in the database
                mycursor.execute("""UPDATE card_data SET company_name=%s,card_holder=%s,designation=%s,mobile_number=%s,email=%s,website=%s,area=%s,city=%s,state=%s,pin_code=%s
                                    WHERE card_holder=%s""", (company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,selected_card))
                mydb.commit()
                st.success("Information updated in database successfully.")

        with column2:
            mycursor.execute("SELECT card_holder FROM card_data")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
            st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
            st.write("#### Proceed to delete this card?")
    except:
        st.warning("There is no data available in the database")
        
st.button("Delete", key='switch_button')

if SELECT=="Deletion":
    st.subheader("Delete Record")
    if st.button("Yes Delete Business Card"):
                mycursor.execute(f"DELETE FROM card_data WHERE card_holder='{selected_card}'")
                mydb.commit()
                st.success("Business card information deleted from database.")
