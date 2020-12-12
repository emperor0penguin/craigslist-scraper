# -*- coding: utf-8 -*-
"""

"""
import requests
from html.parser import HTMLParser
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Listing:
    def __init__(self, post_id):
        self.post_id = post_id

    def __str__(self):
        return f'Post ID: {self.post_id}, URL: {self.url}, Title: {self.title}, Time: {self.time}, ${self.price}'

class SearchParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.listings = []
        self.listing = None
        self.is_price = False
        self.is_title = False
        self.is_total_count = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'li' and 'class' in attrs and attrs['class'] == 'result-row':
            self.listing = Listing(int(attrs['data-pid']))
        elif self.listing is not None:
            if tag == 'a':
                if not hasattr(self.listing, 'url'):
                    self.listing.url = attrs['href']
                elif 'result-title' in attrs['class']:
                    self.is_title = True
            elif tag == 'time':
                self.listing.time = attrs['datetime']
            elif tag == 'span' and attrs['class'] == 'result-price':
                self.is_price = True
        elif tag == 'span' and 'class' in attrs and attrs['class'] == 'totalcount':
            self.is_total_count = True

    def handle_data(self, data):
        if self.is_title:
            self.listing.title = data
            self.is_title = False
        if self.is_price:
            self.listing.price = int(data[1:].replace(',',''))
            self.is_price = False
        elif self.is_total_count:
            self.total_count = int(data)

    def handle_endtag(self, tag):
        if self.listing is not None and tag == 'li':
            self.listings.append(self.listing)
            self.listing = None
        elif tag == 'span' and self.is_total_count:
            self.is_total_count = False

class PostParser(HTMLParser):
    SMALL_END = '50x50c.jpg'
    LARGE_END = '600x450.jpg'

    def __init__(self):
        super().__init__()
        self.imgs = []
        self.is_description = False
        self.description = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img':
            url = attrs['src']
            if url.endswith(self.SMALL_END):
                url = url[:-len(self.SMALL_END)] + self.LARGE_END
            self.imgs.append(url)
        elif tag == 'section' and 'id' in attrs and attrs['id'] == 'postingbody':
            self.is_description = True

    def handle_data(self, data):
        if self.is_description and 'QR Code Link' not in data:
            self.description += data

    def handle_endtag(self, tag):
        if tag == 'section' and self.is_description:
            self.is_description = False

def write_file(post_ids):
        with open('post_history.txt', 'w') as out_file:
            for post_id in post_ids:
                out_file.write(f'{post_id}\n')

def read_file():
    with open('post_history.txt', 'r') as in_file:
        return {int(post_id) for post_id in in_file}

def send_message(listing):
    title = listing.title
    price = listing.price
    url = listing.url

    sender_email = '@gmail.com'
    receiver_email = '@mms.cricketwireless.net'
    password = ''

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = title


    filename = 'image.jpg'  # In same directory as script

    # Open image file in binary mode
    with open(filename, 'rb') as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        'Content-Disposition',
        f'attachment; filename= {filename}',
    )
    part.add_header('Content-ID', 'img1')
    # Add body to email
    message.attach(MIMEText(f'price: ${price} \n{url}', 'plain'))

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()



    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

def get_listings():
    url = 'https://austin.craigslist.org/search/bia?hasPic=1&search_distance=20&postal=78613'
    parser = SearchParser()
    parser.feed(requests.get(url).text)
    total_count = parser.total_count
    all_listings = parser.listings
    while len(all_listings) < total_count:
        parser = SearchParser()
        parser.feed(requests.get(f'{url}&s={len(all_listings)}').text)
        all_listings.extend(parser.listings)
    return all_listings

def get_image(listing):
    parser = PostParser()
    parser.feed(requests.get(listing.url).text)
    if len(parser.imgs) == 0:
        return None
    with requests.get(parser.imgs[0], stream=True) as response:
        return response.raw.read()



def main():
    old_ids = read_file()
    current_listings = get_listings()
    new_listings = [l for l in current_listings if l.post_id not in old_ids]
    for listing in new_listings:
        get_image(listing)
        #send_message(listing)
        print(str(f'title: {listing.title}'))
    write_file(l.post_id for l in current_listings)


if __name__ == "__main__":
    main()
