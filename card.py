import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import  mysql.connector
from PIL import Image
import cv2
import os
import matplotlib.pyplot as plt
import re

#easy OCR
reader = easyocr.Reader(['en'])

# CONNECTING WITH MYSQL DATABASE
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root02",
    database= "bizcard_data"
                )
mycursor = mydb.cursor()
query='''CREATE TABLE IF NOT EXISTS card_data
                (Card_Holder_Name TEXT,
                    Designation TEXT,
                    Company_Name TEXT,
                    Phone_Number VARCHAR(50),
                    Email TEXT,
                    Website TEXT,
                    Area VARCHAR(50), 
                    City TEXT,
                    State TEXT,
                    Pincode VARCHAR(10),
                    Image LONGBLOB
                    )'''
mycursor.execute(query)
mydb.commit()

#streamlit page background setup
page_bg_img='''
<style>
[data-testid="stAppViewContainer"]{
        background-color:#F4C1E8;   
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
        options = ["About","Upload Image","Make Changes","Deletion"],
        icons =["database","image","vector-pen","eraser"],
        default_index=2,
        orientation="horizontal",
        styles={"container": {"padding": "0!important", "background-color": "white","size":"cover", "width": "100%"},
                "icon": {"color": "black", "font-size": "20px"},
                "nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px", "--hover-color": "#b0abac"},
                "nav-link-selected": {"background-color": "#b0abac"}})

if SELECT=="About":
    st.subheader("About the Application")
    st.write(" Users can save the information extracted from the card image using easy OCR. The information can be uploaded into a database (MySQL) after alterations that supports multiple entries. ")
    st.subheader("What is Easy OCR?")
    st.write("Easy OCR is user-friendly Optical Character Recognition (OCR) technology, converting documents like scanned paper, PDFs, or digital camera images into editable and searchable data. A variety of OCR solutions, including open-source libraries, commercial software, and cloud-based services, are available. These tools are versatile, used for extracting text from images, recognizing printed or handwritten text, and making scanned documents editable.")
    st.subheader("Existing Data in Database")
    mycursor.execute('''Select Card_Holder_Name,Designation,Company_Name,
                Phone_Number,Email,Website,Area,City,State,Pincode from card_data''')
    updated_df = pd.DataFrame(mycursor.fetchall(),
                columns=["Card Holder Name","Designation","Company Name",
                "Phone Number", "Email","Website", "Area", "City", "State", "Pin_Code"])
    st.write(updated_df)

if SELECT=="Upload Image": 
    st.subheader(":black[Business Card]")
    image_files = st.file_uploader("Upload the Business Card below:", type=["png","jpg","jpeg"])
    def save_card(image_files):
        uploaded_cards_dir = os.path.join(os.getcwd(),"bizcard")
        with open(os.path.join(uploaded_cards_dir, image_files.name), "wb") as f:
            f.write(image_files.getbuffer())

    if image_files != None:
        col1, col2 = st.columns(2, gap="large")
        with col1:
            img = image_files.read()
            st.markdown("### Business Card has been uploaded")
            st.image(img, caption='The image has been uploaded successfully',width=500)
            save_card(image_files)
            
        with col2:
            saved_img = os.getcwd() + "\\" + "bizcard" + "\\" + image_files.name
            image = cv2.imread(saved_img)
            res = reader.readtext(saved_img)
            st.markdown("Data has been extracted from images")
            def image_preview(image, res):
                for (bbox, text, prob) in res:
                    # unpack the bounding box
                    (tl, tr, br, bl) = bbox
                    tl = (int(tl[0]), int(tl[1]))
                    tr = (int(tr[0]), int(tr[1]))
                    br = (int(br[0]), int(br[1]))
                    bl = (int(bl[0]), int(bl[1]))
                    cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                    cv2.putText(image, text, (tl[0], tl[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                plt.rcParams['figure.figsize'] = (15, 15)
                plt.axis('off')
                plt.imshow(image)
            b=image_preview(image, res)
            st.set_option('deprecation.showPyplotGlobalUse', False)
            st.pyplot(b)
        
        # easy OCR
        saved_img = os.getcwd() + "\\" + "bizcard" + "\\" + image_files.name
        result = reader.readtext(saved_img, detail=0, paragraph=False)
        
        # CONVERTING IMAGE TO BINARY TO UPLOAD TO SQL DATABASE
        def img_to_binary(file):
            # Convert image data to binary format
            with open(file, 'rb') as file:
                binaryData = file.read()
            return binaryData
        
        
        data = {"Card_Holder_Name":[],
                "Designation":[],
                "Company_Name":[],
                "Phone_Number":[],
                "Email":[],
                "Website":[],
                "Area":[],
                "City":[],
                "State":[],
                "Pincode":[],
                "image": img_to_binary(saved_img)
                }

        def get_data(res):
            for ind, i in enumerate(res):
                
                # To get WEBSITE_URL
                if "www " in i.lower() or "www." in i.lower():
                    data["Website"].append(i)
                elif "WWW" in i:
                    data["Website"] = res[4] + "." + res[5]

                # To get EMAIL ID
                elif "@" in i:
                    data["Email"].append(i)
                    
                # To get MOBILE NUMBER
                elif "-" in i:
                    data["Phone_Number"].append(i)
                    if len(data["Phone_Number"]) == 2:
                        data["Phone_Number"] = " & ".join(data["Phone_Number"])
                # To get COMPANY NAME
                elif ind == len(res) - 1:
                    data["Company_Name"].append(i)

                # To get CARD HOLDER NAME
                elif ind == 0:
                    data["Card_Holder_Name"].append(i)
                    
                # To get DESIGNATION
                elif ind == 1:
                    data["Designation"].append(i)
                    
                # To get AREA
                if re.findall('^[0-9].+, [a-zA-Z]+', i):
                    data["Area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+', i):
                    data["Area"].append(i)
                
                # To get CITY NAME
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*', i)
                if match1:
                    data["City"].append(match1[0])
                elif match2:
                    data["City"].append(match2[0])
                elif match3:
                    data["City"].append(match3[0])
                    
                # To get STATE
                state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
                if state_match:
                    data["State"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
                    data["State"].append(i.split()[-1])
                if len(data["State"]) == 2:
                    data["State"].pop(0)

                # To get PINCODE
                if len(i) >= 6 and i.isdigit():
                    data["Pincode"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]', i):
                    data["Pincode"].append(i[10:])
        get_data(result)
        df = pd.DataFrame(data)
        st.success("### Data Extracted!")
        st.write(df)
        
        if st.button("Upload to Database"):
            for i, row in df.iterrows():
                query1='''insert into card_data(Card_Holder_Name,Designation,Company_Name,
                Phone_Number,Email,Website,Area,City,State,Pincode,Image)
                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                mycursor.execute(query1, tuple(row))
                mydb.commit()
                mycursor.execute('''Select Card_Holder_Name,Designation,Company_Name,
                Phone_Number,Email,Website,Area,City,State,Pincode from card_data''')
                updated_df = pd.DataFrame(mycursor.fetchall(),
                columns=["Card Holder Name","Designation","Company Name",
                "Phone Number", "Email","Website", "Area", "City", "State", "Pin_Code"])
                st.success("#### Uploaded to database successfully!")
                st.write(updated_df)
                
    
elif SELECT=="Make Changes":
    st.markdown(":black[Alter the data here]")
    try:
            mycursor.execute("SELECT Card_Holder_Name FROM card_data")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            options = ["Select Card"] + list(business_cards.keys())
            selected_card = st.selectbox("**Select a card**", options)
            if selected_card == "Select Card":
                st.write("Card not selected")
            else:
                st.markdown("#### Update or modify the data below")
                mycursor.execute('''Select Card_Holder_Name,Designation,Company_Name,
                Phone_Number,Email,Website,Area,City,State,Pincode from card_data WHERE Card_Holder_Name=%s''',
                (selected_card,))
                result = mycursor.fetchone()

                # DISPLAYING ALL THE INFORMATIONS
                company_name = st.text_input("Company_Name", result[2])
                card_holder = st.text_input("Card_Holder", result[0])
                designation = st.text_input("Designation", result[1])
                mobile_number = st.text_input("Mobile_Number", result[3])
                email = st.text_input("Email", result[4])
                website = st.text_input("Website", result[5])
                area = st.text_input("Area", result[6])
                city = st.text_input("City", result[7])
                state = st.text_input("State", result[8])
                pin_code = st.text_input("Pin_Code", result[9])



                if st.button(":black[Commit changes to DB]"):
                    
                    # Update the information for the selected business card in the database
                    mycursor.execute("""UPDATE card_data SET Card_Holder_Name=%s,Designation=%s,Company_Name=%s,Phone_Number=%s,Email=%s,Website=%s,
                                    Area=%s,City=%s,State=%s,Pincode=%s where Card_Holder_Name=%s""",
                                    (card_holder,designation,company_name, mobile_number, email, website, area, city, state, pin_code,
                    selected_card))

                    mydb.commit()
                    st.success("Information updated in database successfully.")

            if st.button(":black[View data]"):
                mycursor.execute('''Select Card_Holder_Name,Designation,Company_Name,
                Phone_Number,Email,Website,Area,City,State,Pincode from card_data''')
                updated_df2 = pd.DataFrame(mycursor.fetchall(),
                                        columns=["Card_Holder_Name","Designation","Company_Name",
                "Phone_Number","Email","Website","Area","City","State","Pincode"])
                st.write(updated_df2)
    except:
                st.warning("There is no data available in the database")
            
if SELECT == "Deletion":
        st.subheader(":black[Delete the data]")
        try:
            mycursor.execute("SELECT Card_Holder_Name FROM card_data")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            options = ["None"] + list(business_cards.keys())
            selected_card = st.selectbox("**Select a card**", options)
            if selected_card == "None":
                st.write("No card selected")
            else:
                st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
                st.write("#### Proceed to delete this card?")
                if st.button("Confirm deletion"):
                    mycursor.execute(f"DELETE FROM card_data WHERE Card_Holder_Name='{selected_card}'")
                    mydb.commit()
                    st.success("Business card information has been deleted from database")
            
            if st.button(":black[View data]"):
                mycursor.execute('''Select Card_Holder_Name,Designation,Company_Name,
                    Phone_Number,Email,Website,Area,City,State,Pincode from card_data''')
                updated_df3 = pd.DataFrame(mycursor.fetchall(),
                                            columns=["Card_Holder_Name","Designation","Company_Name",
                    "Phone_Number","Email","Website","Area","City","State","Pincode"])
                st.write(updated_df3)
        except:
            st.warning("There is no data available in the database")
