#/usr/bin/env python
#coding=utf8
'''
Created on 2015年8月10日

@author: liangc
'''
  
from service.core_service import CoreService,ttypes,constants 

from thrift import Thrift  
from thrift.transport import TSocket  
from thrift.transport import TTransport  
from thrift.protocol import TBinaryProtocol  
from thrift.protocol import TCompactProtocol  
from thrift.server import TServer  
import time,os,sys,json
# local config
import config 
import logging

# for mail
import smtplib  
from email.mime.text import MIMEText  
from email.header import Header

logfile = config.LOG_FILE
logger = logging.getLogger()
hdlr = logging.FileHandler(logfile)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

# 实现类  
class HandlerImpl :  
    '''
    TODO 150810 : 把 smtp 做成长连接，是以后的优化任务
    发送邮件的参数结构 json = 
        {
            "sender":"发送人邮箱",
            "receiver":"接收人邮箱",
            "subject":"邮件主题",
            "content":"邮件内容"
        }
    '''
    def process(self, licence, json_args):
        logger.debug('licence=%s ; json=%s' % (licence,json_args)) 
        success = dict(success=True)
        try :
            obj = json.loads(json_args)
            subject = obj['subject']
            content = obj['content'] 
            if obj.get('sender'):
                sender = obj['sender']
            else:
                sender = config.DEF_SENDER
            receiver = obj['receiver']
            smtp = smtplib.SMTP()
            msg = MIMEText(content,'plain','utf-8')
            msg['Subject'] = Header(subject, 'utf-8') 
            smtp.connect(config.SMTP)
            success['entity'] = smtp.sendmail(sender, receiver, msg.as_string())  
            smtp.quit()  
        except Exception as e:
            logger.error(e)
            success = dict(success=False,entity={"reason":"exception"})
        return json.dumps(success) 

    
handler = HandlerImpl()  

def timestamp():
    return int(time.time()*1000)

if __name__ == '__main__' :
    handler = HandlerImpl()  
    processor = CoreService.Processor(handler)
    transport = TSocket.TServerSocket(config.HOST,int(config.PORT))
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
    print 'Starting server on %s' % (config)
    print 'pid=%s ; host=%s ; port=%s' % (os.getpid(),config.HOST,config.PORT)
    server.serve()