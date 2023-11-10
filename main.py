# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 12:47:18 2023

@author: above
"""

import streamlit as st
import smtplib
from email.message import EmailMessage
import ssl
import pandas as pd



#carreguem dades
@st.cache_data(ttl="1d")
def load_data(sheets_url):
    xlsx_url = sheets_url.replace("/edit#gid=", "/export?format=xlsx&gid=")
    return pd.read_excel(xlsx_url)


logo_OCTE = "logo Transició Energètica.png"
logo_CCAC ="CCAC_H_col.jpg"
logo_ICAEN ="log icaen.png"
st.sidebar.image(logo_OCTE)
st.sidebar.image(logo_CCAC)
st.sidebar.image(logo_ICAEN)

llista_municipis = load_data(st.secrets["public_gsheets_url_basics"])
calendari = load_data(st.secrets["public_gsheets_url_calendari"])
calendari1 = calendari.set_index(['Municipi','Data','mes','Dia'])


calendari1=calendari1.replace(not(False), True)

st.title("Sol·licitud atenció ciutadana")




atencio = st.selectbox("Escull tipus d'atenció",("Presencial","Correu"))



if atencio=="Presencial":
    st.write("Estàs sol·licitant una atenció presencial, a continuació podràs sol·licitar una cita en funció del lloc i la data.")
elif atencio=="Correu":
    st.write("Estàs sol·licitant una atenció per correu, exposa el tema a continuació i et respondrem tan aviat com puguem.")
else:
    st.write("Escull el tipus d'atenció que requereixes.")
    
# Recopila la informació de l'usuari
col1,col2,col3=st.columns(3)
with col1:
    nom=st.text_input("nom i cognoms")
with col2:
    correu_electronic=st.text_input("correu electrònic")
with col3:
    municipi = st.selectbox('Escull municipi', llista_municipis['Municipi'].drop_duplicates())

motiu = st.selectbox("Escull el motiu de la consulta...", ["Factura energètica", "Autoconsum", "Rehabilitació", "Altres"])


if atencio=="Presencial":
    
    st.header("Selecció de Franja Horaria")
    
    col1,col2=st.columns(2)
    with col1:
        lloc_sessió = st.selectbox("municipi de trobada",["Valls","Alcover","Vallmoll","Vila-rodona","Pla de Santa Maria"])
    with col2:
        mes = st.selectbox("Escull mes...",("gener","febrer","març","abril","maig","juny","juliol","agost","setembre","octubre","novembre","desembre"))
    
    
    calendari2 = calendari1[calendari1.index.get_level_values(2)==mes].loc[lloc_sessió]
    llistat_dies = [calendari2.index.get_level_values(2)[i] + " de " + calendari2.index.get_level_values(1)[i] +" del " + str(calendari2.index.get_level_values(0)[i].year) for i in range(len(calendari2))]
    dia_escollit = st.selectbox("Dies disponibles al " +mes, llistat_dies)
    
    calendari3=calendari2[calendari2.index.get_level_values(0)==calendari2.index.get_level_values(0)[llistat_dies.index(dia_escollit)]]
    
    dia = calendari3.index[0][2]
    st.write("A continuació tens les franges disponibles per al **"+dia_escollit+"**, sel·lecciona quina franja vols")
    
    # Crear una lista de franjas horarias
    hores = pd.DataFrame(data=calendari3.values,index=['A'],columns=calendari3.columns)
    hores = hores.transpose().query("A == 'buit'")
    
    # Crear una casilla de verificación para seleccionar la franja horaria
    franja_seleccionada = st.radio("Selecciona una franja horaria:", hores.index).strftime("%H:%M")    
    
    st.write("Un cop enviat el correu rebràs una confirmació de reunió a **"+lloc_sessió+ " pel "+dia_escollit+" a les "+franja_seleccionada+"**.")
    
    subject = ""
    message = st.text_input("Afegeix una petita descripció:")
    message = nom+"\n"+correu_electronic+"\n"+municipi+"\n"+motiu+"\n"+message+"\n"+lloc_sessió+ " pel "+dia+" de "+mes+" a les "+franja_seleccionada

elif atencio=="Correu":
    subject = st.text_input("Assumpte:")
    message = st.text_area("Indica aqui la teva consulta:")
    message = nom+"\n"+correu_electronic+"\n"+municipi+"\n"+motiu+"\n"+message

    



subject = municipi + "_" + atencio + "_atenció ciutadania_" + subject



if st.button("Enviar Correu"):
    # Configura el servidor de correu 
    email_sender= st.secrets["email_sender"]
    password = st.secrets["email_password"]
    email_receiver = st.secrets["email_receiver"]
    

    # Crea el missatge
    em = EmailMessage()
    em["From"]=email_sender
    em["To"]=email_receiver
    em["Subject"]=subject
    em.set_content(message)
    
    context = ssl.create_default_context()


    # Inicia una conexió segura amb el servidor SMTP
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com",465,context = context) as smtp:
            smtp.login(email_sender,password)
            smtp.sendmail(email_sender,email_receiver,em.as_string())
        st.success("El correu s'ha enviat correctament, rebrà una confirmació de l'hora")
    except Exception as e:
        st.error("Hi ha hagut un error en enviar la sol·licitud, posis en contacte amb l'oficina a través del correu energia@altcamp.cat")


