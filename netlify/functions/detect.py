netlify/functions/detect.pyimport json
import base64
import requests
import os

def get_access_token():
    # 从 Netlify 环境变量中获取凭证，避免泄露 [4]
    api_key = os.environ.get("BAIDU_API_KEY")
    secret_key = os.environ.get("BAIDU_SECRET_KEY")
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": api_key, "client_secret": secret_key}
    res = requests.post(url, params=params).json()
    return res.get("access_token")

def handler(event, context):
    # 仅允许 POST 请求
    if event['httpMethod'] != 'POST':
        return {"statusCode": 405, "body": "Method Not Allowed"}

    try:
        # 获取前端传来的 Base64 图片数据
        body = json.loads(event['body'])
        img_base64 = body.get("image")

        # 调用百度人脸检测接口 [5]
        token = get_access_token()
        url = f"https://aip.baidubce.com/rest/2.0/face/v3/detect?access_token={token}"
        
        # 必须指定 face_field 包含 beauty 才能获取颜值分 [5, 6]
        payload = json.dumps({
            "image": img_base64,
            "image_type": "BASE64",
            "face_field": "beauty,age,gender"
        })
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, headers=headers, data=payload)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response.json())
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
