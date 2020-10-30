'''
필요한 기능
1. 페이지가 로딩되고 나면 DB에 저장되어 있는 기사정보를 받아와 카드로 만들어 붙인다
- 페이지 로딩 후 함수가 실행되어야 함
- 서버로 get요청을 보낸다
- 서버는 db에서 기사의 제목, 설명, url, 이미지url, 코멘트를 받아와 넘겨준다
- 받아온 정보로 카드를 만들어 붙인다

2. 포스팅 버튼을 누르면 입력한 url과 코멘트를 받아 db에 제목, 설명, 이미지url까지
저장하고 페이지를 새로고침한다.
- 포스팅 버튼을 눌러 함수가 실행되게한다
- url과 코멘트가 다 입력됐는지 확인하다
- 입력받은 url과 코멘트를 서버로 POST요청보낸다.
- 서버에서 url과 코멘트를 받아 제목, 설명, 이미지url을 크롤링한다
- 5개 정보를 db에 저장한다
- 성공메세지 반환하며 페이지를 새로고침한다.
'''

from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.swjungle

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/memo', methods=['GET'])
def listing():
    # db의 모든 데이터 리스트에 넣어오기
    result = list(db.articles.find({}, {'_id':0}))
    return jsonify({'result':"success", 'message':'GET통신성공', 'articles':result})

@app.route('/memo', methods=['POST'])
def posting():
    # 클라이언트로부터 url, comment 받아오기
    url = request.form['url_give']
    comment = request.form['comment_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    
    # 메타태그 스크래핑하기
    og_title = soup.select_one('meta[property="og:title"]')['content']
    og_image = soup.select_one('meta[property="og:image"]')['content']
    og_description = soup.select_one('meta[property="og:description"]')['content']

    # db에 저장하기
    article = {
            'url' : url,
            'title' : og_title,
            'desc' : og_description,
            'image' : og_image,
            'comment' : comment
    }
    db.articles.insert_one(article)
    return jsonify({'result':'success', 'message':'POST통신성공'})

# flask 서버가 모든 ip에 대한 접근을 허용하고 5000번 포트 사용한다,
# 디버그 모드를 True로 해놓으면 코드변경을 감지하고 자동으로 리로드해서 서버를 올린다
if __name__ == '__main__':
   app.run(host='0.0.0.0',port=5000,debug=True)