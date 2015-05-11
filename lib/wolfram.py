# -*- coding: utf-8 -*-
""" The following variable smust be set in the .rive file before calling the function
    # i18n
    LANG = "fr"
    ERROR_MSG = u"Je n'ai pas pu trouver de réponse. L'erreur est "
    ERROR_MSG_NONE = u"Je n'ai pas pu trouver de réponse."
    ERROR_MSG_NOT_CONFIGURED = u"Le package brain wolfram doit être configuré."
    ERROR_MSG_CONFIG = u"Une erreur est survenue pendant la récupération de la configuration."
"""

# imports
import traceback
import goslate
import tungsten
import pprint


# translation for non "us" languages as wolfram works only in english
class Wolfram():

    def __init__(self, cfg_i18n):
        """ constructor
            @param cfg_i18n : a dictionnary of i18n data
            { 'LANG' : ...,
              'ERROR_MSG' : ...,
              'ERROR_MSG_NONE' : ...,
              'ERROR_MSG_NOT_CONFIGURED' : ...,
              'ERROR_MSG_CONFIG' : ... }
        """
        self.cfg_i18n = cfg_i18n

    def query(self, args):
        """ Do the query
            @param args : args from rivescript
        """
        # config
        # sample (and wrong) value : WOLFRAMALPHA_APPID = "GHJ4YD-KSDFUEHEJL"
        try:
            from domogik.common.queryconfig import QueryForBrain
            config = QueryForBrain()
            self.WOLFRAMALPHA_APPID = config.query("brain", "wolfram", 'api_key')
            if self.WOLFRAMALPHA_APPID == None:
                return self.cfg_i18n['ERROR_MSG_NOT_CONFIGURED']
        except:
            return self.cfg_i18n['ERROR_MSG_CONFIG']
        query = ' '.join(args)
        query_us = self.translate_query(query)
        response = self.ask_wolfram(query_us)
        response_lang = self.translate_response(response)
        return response_lang

    def translate_query(self, text):
        #print("Translate query : {0}".format(text))
        if self.cfg_i18n['LANG'] == "us":
            return text
    
        # translation in "us"
        gs = goslate.Goslate()
        translated = gs.translate(text, "us", self.cfg_i18n['LANG'])
        return translated
    
    def translate_response(self, text):
        #print("Translate response : {0}".format(text))
        if self.cfg_i18n['LANG'] == "us":
            return text
    
        # translation in LANG
        gs = goslate.Goslate()
        translated = gs.translate(text, self.cfg_i18n['LANG'])
        return translated
    
    # request wolfram for an answer
    def ask_wolfram(self, text):
        try:
            response = u""
            #print("Call Wolfram for : {0}".format(text))
            client = tungsten.Tungsten(self.WOLFRAMALPHA_APPID)
            result = client.query(text)
            if result.success == False:
                #print(result.error)
                if result.error == None:
                    return u"{0}".format(self.cfg_i18n['ERROR_MSG_NONE'])
                else:
                    return u"{0} : {1}".format(self.cfg_i18n['ERROR_MSG'], result.error)
    
            # first, search if there is a id=Result
            # if so, we only take this one in account
            for pod in result.pods:
                if pod.id == "Result":
                    print(pod.format)
                    return u"{0}".format(self.process_response(pod.format['plaintext']))
    
            # if no result, process returned data
            for pod in result.pods:
                # skip id=Input
                if pod.id == "Input":
                    continue
                data = pod.format
                # skip data with no plain text
                if data['plaintext'] == [None]:
                    continue
                print(u"Title = {0}".format(pod.title))
                print(u"Text = {0}".format(data['plaintext']))
    
                pod_result = self.process_response(data['plaintext'])
                response = u"{0}\n{1}. {2}".format(response, pod.title, pod_result)
            return response
        except:
            print(u"Wolfram Error : {0}".format(traceback.format_exc()))
            return u"{0} : {1}".format(self.cfg_i18n['ERROR_MSG'], traceback.format_exc())
    
    def process_response(self, tab_text):
        ### make a nice output
        # 1. we concatenate all the returned list elements
        # todo : a \n instead of the space ?
        # we can't do this as the list may contain some None... : tmp_pod_data = '\n'.join(tab_text)
        tmp_pod_data = u''
        for tmp in tab_text:
            print(tmp)
            if tmp != None:
                tmp_pod_data = u'{0}\n{1}'.format(tmp_pod_data, tmp)
        print(tmp_pod_data)
    
        # 2. we split by \n. 
        tmp_pod_data_lines = tmp_pod_data.split("\n")
        print(tmp_pod_data_lines)
        
        # 3. for each line we spit by | (for tables)
        pod_result = u""
        for a_line in tmp_pod_data_lines:
            print(a_line)
            a_line = a_line.replace("|", ":")
            pod_result = u"{0}{1}. ".format(pod_result, a_line)
        return pod_result
                     
    
    
    
