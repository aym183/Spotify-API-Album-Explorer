'''
This project has been done using the Spotify API. It is a very simple GUI which enables the user to search
for their favourite artists, explore each and every one of their albums and each song in the album

'''
from tkinter import *
import base64
import requests
import datetime
from urllib.parse import urlencode
import json
import numpy as np

# Credentials to gain access to the API

client_id = 'a1aa4cbceee64b4ba6d774050bfaaa92'
client_secret =  #classified#

Artist_search = {}

Album_search = {}

Songs_search = []

# Entire class mainly used for providing authorisation of API and easy access to tokens, headers etc

class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = 'https://accounts.spotify.com/api/token'
    
    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        
    def get_client_credentials(self):
        client_id = self.client_id  
        client_secret =  self.client_secret 
        if client_id == None or client_secret == None:
            raise Exception("Please Fill In Both")
            
        client_creds =  "{}:{}".format(client_id, client_secret)
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()
    def get_token_header(self):
       
        client_creds_b64 = self.get_client_credentials()
        return {
                'Authorization': f'Basic {client_creds_b64} ' 
                }
        
    def get_token_data(self):
        return {
                'grant_type' : 'client_credentials' 
                }
        
    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {
            'Authorization' : f"Bearer {access_token}"
        }
        return headers

        
    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_header = self.get_token_header()
        r = requests.post(token_url, data = token_data, headers = token_header)
        
        if r.status_code not in range(200,299) :
            raise Exception("Could not authenticate client")
        now = datetime.datetime.now() #just to check if token expired 
        data = r.json()
        access_token = data['access_token']
        expires_in =  data['expires_in'] #seconds
        expires = now + datetime.timedelta(seconds = expires_in)
        self.access_token = access_token
        self.access_token_expires = expires 
        self.access_token_did_expire = expires< now
        return True 
    
    def get_access_token(self):
     
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires<now:
            self.perform_auth()
            return self.get_access_token()
        elif token==None:
            self.perform_auth()
            return self.get_access_token()
            
        return token 
    
    
    # Function shows search results for artists
    
    def get_artist(self):
         
        headers = self.get_resource_header()


        my_dict = {}
        endpoint = 'https://api.spotify.com/v1/search'
        data = urlencode({"q": Artist_Search_Box.get(), 'type': "artist","market": "US", "limit": "10"}) # urlencode used to change to url format
        lookup_url = "{}?{}".format(endpoint, data)
              
        request = requests.get(lookup_url, headers = headers).text
        response = json.loads(request)
        for i in range(len(response.get('artists').get('items'))):

            my_dict[f"{response.get('artists').get('items')[i].get('name')}"] = [response.get('artists').get('items')[i].get('id')] # , new_response.get('artists').get('items')[i].get('images')[2].get('url')]
            if len(response.get('artists').get('items')[i].get('images')) == 0:
                my_dict[f"{response.get('artists').get('items')[i].get('name')}"].append("NO IMAGE!")
            else:

                my_dict[f"{response.get('artists').get('items')[i].get('name')}"].append(f"{response.get('artists').get('items')[0].get('images')[2].get('url')}")
        Artist_Search_Results_Listbox.delete(0,'end')
       
        for i in my_dict:
            
            Artist_search[i] = my_dict.get(i)[0]
            Artist_Search_Results_Listbox.insert(END, i)
        


    
        
        

    
client = SpotifyAPI(client_id, client_secret)    

# Part of dependent listbox that shows artist search results and once any of the results are clicked
# The albums of those artists are shown

def pick_artist(e):
    
    
    client = SpotifyAPI(client_id, client_secret)
    headers = client.get_resource_header()
    
    if Artist_Search_Results_Listbox.get(ANCHOR) in Artist_search:
        new_endpoint = 'https://api.spotify.com/v1/artists/'    
        data2 = {'ids': Artist_search.get(Artist_Search_Results_Listbox.get(ANCHOR))}
        data = urlencode({"include_groups": "album" , "market": 'US'})
        lookup2_url = f"{new_endpoint}{data2.get('ids')}/albums?{data}"
            
        request2 = requests.get(lookup2_url, headers = headers).text
        new_response = json.loads(request2)

        new_dict = {}
        for i in range(len(new_response.get('items'))):
                if new_response.get('items')[i].get('name') not in new_dict.keys():
                    new_dict[f"{new_response.get('items')[i].get('name')}"] = [new_response.get('items')[i].get('id')]
                    if len(new_response.get('items')[i].get('images')[1].get("url")) ==0 :
                        new_dict[new_response.get('items')[i].get('name')].append("NO IMAGE!")
                    else:
                        new_dict[new_response.get('items')[i].get('name')].append(new_response.get('items')[i].get('images')[1].get("url"))

        Albums_And_Songs_Listbox.delete(0,'end')
        
        if len(new_dict)==0:
            text = "No Albums!"
            Albums_And_Songs_Listbox.insert(END, text)
        
        else:

            for i in new_dict:
                Album_search[i] = new_dict.get(i)[0]
                Albums_And_Songs_Listbox.insert(END, i)
                
                
# Part of albums listbox that once clicked, shows the songs in the album
def pick_album(e):
    if Albums_And_Songs_Listbox.get(ANCHOR) in Album_search:
        
        client = SpotifyAPI(client_id, client_secret)
        headers = client.get_resource_header()

        token_url = 'https://api.spotify.com'  #v1/albums/{id}
        data = {"ids": Album_search.get(Albums_And_Songs_Listbox.get(ANCHOR))}
        data2 = urlencode({"market": "US"})
        end_url = f"{token_url}/v1/albums/{data.get('ids')}"
            
        final = f"{end_url}?{data2}"

        request3 = requests.get(final, headers = headers).text
        new_response2 = json.loads(request3)
    
        Albums_And_Songs_Listbox.delete(0,'end')
        for i in range(len(new_response2.get('tracks').get('items'))):
            response = new_response2.get('tracks').get('items')[i].get('name')
            Albums_And_Songs_Listbox.insert(END, response)


# Formation of GUI

root = Tk()
root.title("Artist Album Explorer")
root.geometry('850x400')

# Null Labels are used for accurate spacing

Null_Label = Label(root, text = " ")
Null_Label.grid(row = 0, column = 0)

# Button used after input entered to get search results

Artist_Search_Button = Button(root, text="Search",command = client.get_artist, fg="blue")
Artist_Search_Button.grid(row= 0, column = 4)

Null_Label  = Label(root, text = " ")
Null_Label.grid(row = 0, column = 1)


Null_Label  = Label(root, text = " ")
Null_Label.grid(row = 0, column = 2)

Input_Box_Label = Label(root, text = "Please Enter Artist:")
Input_Box_Label.grid(row = 0, column = 2)

Artist_Search_Box = Entry(root)
Artist_Search_Box.grid(row=0, column = 3)

Null_Label = Label(root, text = " ")
Null_Label.grid(row = 1, column = 2)

# The listbox on the left of the GUI that shows the search results of the Artists

Artist_Search_Results_Listbox = Listbox(root, bg = 'coral', height = 15, width = 30)
Artist_Search_Results_Listbox.grid(row = 2, column =2, padx =20)

                                    #my_listbox
Null_Label = Label(root, text = "           ")
Null_Label.grid(row = 1, column = 4)

# The listbox on the right of the GUI that shows the Albums and Songs of the artists when artist name clicked
Albums_And_Songs_Listbox = Listbox(root, bg = 'coral', height = 15, width = 30)
Albums_And_Songs_Listbox.grid(row = 2, column =4)

Welcome = "Hi, Welcome To The Album Explorer!"
Artist_Search_Results_Listbox.insert(END, Welcome)

# Making both listboxes dependant on what has been clicked in the listbox 

Artist_Search_Results_Listbox.bind("<<ListboxSelect>>", pick_artist)

Albums_And_Songs_Listbox.bind("<<ListboxSelect>>", pick_album)



Null_Label = Label(root, text = " ")
Null_Label.grid(row = 1, column = 3)


 
root.mainloop()


