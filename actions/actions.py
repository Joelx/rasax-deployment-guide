# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
 
from typing import Any, Text, Dict, List
 
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk import FormValidationAction
from rasa_sdk.types import DomainDict

import random
import math
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import pytorch_cos_sim 
import pickle
import pandas as pd
from tqdm import  tqdm
import numpy as np
from pprint import pprint

BERTmodel_names=['paraphrase-multilingual-MiniLM-L12-v2','medmediani/Arabic-KW-Mdel','Ezzaldin-97/STS-Arabert','distiluse-base-multilingual-cased-v1','sentence-transformers/LaBSE']
# data_path="mydata/BASE8RGPH24V1_all_12_12_ID"
data_path="mydata/BASE8RGPH24V4_all_18_12_ID"
data_path='mydata/BASE8RGPH24V5_all_08_01_ID'

df=pd.read_excel(data_path +'.xlsx')
unique_values_dict = {k[1]: (k[0][0],k[0][1],v,"situation") for k, v in dict(dict(zip(zip(zip(df["Situation_ID"], df["Module_ID"]), df['Situation ']),df["Situation_ID"]))).items() if (pd.notna(v) and v!='')}
## add tags to comparaison dict 
unique_values_dict.update({k[1]: (k[0][0],k[0][1],v,"tags") for k, v in dict(dict(zip(zip(zip(df["Tags_ID"], df["Module_ID"]), df['Tags']),df["Situation_ID"]))).items() if (pd.notna(v) and v!='')})
unique_values_dict.update({k[1]: (k[0][0],k[0][1],v,'situation Tags') for k, v in dict(dict(zip(zip(zip(df["tags_sit_ID"], df["Module_ID"]), df['situation Tags']),df["Situation_ID"]))).items() if (pd.notna(v) and v!='')})
## add section to comparaison dict
unique_values_dict.update({k[1]: (k[0][0],k[0][1],v,"section") for k, v in dict(dict(zip(zip(zip(df["Section_ID"], df["Module_ID"]), df['Section']),df["Situation_ID"]))).items() if (pd.notna(v) and v!='')})
## add question to comparaison
unique_values_dict.update({k[1]: (k[0][0],k[0][1],v,"question") for k, v in dict(dict(zip(zip(zip(df["Question_ID"], df["Module_ID"]), df["Question AI"]),df["Situation_ID"]))).items() if (pd.notna(v) and v!='')})
unique_values_dict = {key: value for key, value in unique_values_dict.items() if not isinstance(key, float) or not math.isnan(key)}
situations_list = list(unique_values_dict.keys())


# Open the file in write mode and write the dictionary content
with open('unique_values_dict.txt', 'w',encoding='utf-8') as file:
    for key, value in unique_values_dict.items():
        file.write(f"{key}: {value}\n")
        file.write(f"-----------------------------------------------------\n")

        
BERTmodel_name=BERTmodel_names[0]
BERT_model=SentenceTransformer(BERTmodel_name )
pkl_path=data_path+BERTmodel_name.split('/')[0]+'situations_embeddings.pkl'

print('################# using MODEL:', BERTmodel_name)
### initialize weights
        # Your dataset or list of situations
try:
            #Load sentences & embeddings from disc
            with open(pkl_path, "rb") as fIn:
                stored_data = pickle.load(fIn)
                situations = stored_data['situations']
                BERT_weights = stored_data['BERT_weights']
                
                print("BERT model found")


except FileNotFoundError:
                # BERT_model=SentenceTransformer(BERTmodel_)
                print("BERT model loaded")
                
                BERT_weights = BERT_model.encode(situations_list, convert_to_tensor=True,show_progress_bar=True)
                print("BERT model fine-tuned")

                #Store sentences & embeddings on disc
                with open(pkl_path, "wb") as fOut:
                    pickle.dump({'situations': unique_values_dict, 'BERT_weights': BERT_weights}, 
                                fOut, protocol=pickle.HIGHEST_PROTOCOL)
                print("BERT model saved")

def get_unique_elements_with_order(input_list):
    return [element for i, element in enumerate(input_list) if element not in input_list[:i]]



def provide_recommendations(user_input,THRESH, n,df,unique_values_dict,BERT_weights):

  
  input_weight=BERT_model.encode(user_input, show_progress_bar = True,convert_to_tensor=True)
  cosine_scores = pytorch_cos_sim(input_weight, BERT_weights)
  cosine_scores = cosine_scores.cpu().numpy()
  sort_ids=np.argsort(cosine_scores)
  selected_ids=np.flip(sort_ids)[0] 
  # print('ordred cos',[cosine_scores[0][i] for i in selected_ids ])
  # print('selected ordred cos',[cosine_scores[0][i] for i in selected_ids if cosine_scores[0][i]>=THRESH])

  ordred_situations= [(situations_list[i],cosine_scores[0][i]) for i in selected_ids if cosine_scores[0][i]>=THRESH]
  ordred_situations_IDs=[{'input_text':user_input,
                          'similar_text':situation[0],
                          'element_ID':unique_values_dict[situation[0]][0], 
                          'module_ID':unique_values_dict[situation[0]][1],
                          'situation_ID':unique_values_dict[situation[0]][2],
                          'category':unique_values_dict[situation[0]][3],
                          "similarity":situation[1]} for situation in ordred_situations]

#   display(pd.DataFrame(ordred_situations_IDs[:n]))
#   pprint(ordred_situations_IDs)
#   df_with_qst=add_qst_ids(df,pd.DataFrame(ordred_situations_IDs[:n]))
  return (pd.DataFrame(ordred_situations_IDs[:n]))
#   return  ordred_situations[:n],ordred_situations_IDs,get_unique_elements_with_order(ordred_situations_IDs)[:n]

# def add_qst_ids(df, df_rslt):
#     ids=[]
#     for index, row in df_rslt.iterrows():

#         if row['category']=='question':
#             ids.append([row["element_ID"]])
#         if row['category']=='tags':
#             ids.append( df[df['Tags_ID']==row["element_ID"]].Question_ID.unique())
#         if row['category']=='situation':
#             ids.append(df[df['Situation_ID']==row["element_ID"]].Question_ID.unique())
#         if row['category']=='section':
#             ids.append(df[df['Section_ID']==row["element_ID"]].Question_ID.unique())
#     df_rslt['ralated_questions']=ids
#     return df_rslt



# def module_recommendations(df_rslt,n=3):
#     module_ids = df_rslt['module_ID'].unique()[:n].tolist()
#     module_names=[df[df.Module_ID==module_id].module.unique().tolist()[0] for module_id in module_ids]
#     df[df.Module_ID.isin(module_ids)].module.unique().tolist()
#     return module_ids,module_names


# def situation_recommendations(df_rslt,module_id,n=3):
#     output_ids=[]
#     situation_IDs = df_rslt[df_rslt['module_ID']==int(module_id)]["situation_ID"].unique().tolist()
#     print('##########situation_IDs',situation_IDs)
#     print(df_rslt[df_rslt.module_ID==int(module_id)]["situation_ID"].unique())
#     for i in situation_IDs:
#         if i!=22 :   
#             if len(output_ids)<n:
#                 output_ids.append(i)

#     situation_names=[df[df.Situation_ID==output_id]["Situation "].unique().tolist()[0] for output_id in output_ids]
#     # df[df.Situation_ID.isin(output_ids)]["Situation "].unique().tolist()
#     print(situation_names)
#     print(output_ids)
#     return output_ids,situation_names
        

# def question_recommendations(df_rslt_with_qst,situation_ID,n=3):
#     questions=[]
#     if df_rslt_with_qst.head(1)["category"].values[0]=="question" :#and df_rslt_with_qst.head(1)["situation_ID"].values[0]==22:

#         questions=df_rslt_with_qst.head(1)["ralated_questions"].values.tolist()
#     questions.extend(df_rslt_with_qst[df_rslt_with_qst['situation_ID']==situation_ID]["ralated_questions"].values.tolist())
#     output=[]
#     reste=[]
#     question_names=[]
#     reste_question=[]
#     for i in questions:
#         for j in i:
#             if len(output)<n and j not in output :
#                 output.append(j)
#                 question_names.append(df[df.Question_ID==int(j)]["Question AI"].unique().tolist()[0])
#             elif len(output)>=n and j not in output and j not in reste:
                 
#                 reste.append(j)
#                 reste_question.append(df[df.Question_ID==int(j)]["Question AI"].unique().tolist()[0])

#     # question_names=df[df.Question_ID.isin(output)]["Question AI"].unique().tolist()
#     return(output,question_names,reste,reste_question)

# def get_responses(question_id):

#     response=df[df.Question_ID==question_id]['Réponse  Quasi-finale'].unique().tolist()
#     return(response)
def add_qst_ids(df, df_rslt):

    ids=[]
    for index, row in df_rslt.iterrows():
        id_=[]

        for i in row["ralated_responses"]:
            id_.append(df[df['response_ID']==int(i)].Question_ID.unique())
        ids.append(id_)
    df_rslt['ralated_questions']=ids

    return df_rslt

def add_resp_ids(df, df_rslt):
    ids=[]
    for index, row in df_rslt.iterrows():

        if row['category']=='question':
            ids.append( df[df['Question_ID']==row["element_ID"]].response_ID.unique())
        if row['category']=='tags':
            ids.append( df[df['Tags_ID']==row["element_ID"]].response_ID.unique())
        if row['category']=='situation Tags':
            ids.append( df[df['tags_sit_ID']==row["element_ID"]].response_ID.unique())
        if row['category']=='situation':
            ids.append(df[df['Situation_ID']==row["element_ID"]].response_ID.unique())
        if row['category']=='section':
            ids.append(df[df['Section_ID']==row["element_ID"]].response_ID.unique())
    df_rslt['ralated_responses']=ids
    return df_rslt

def module_recommendations(df_rslt,n=3):
    module_ids = df_rslt['module_ID'].unique()[:n].tolist()
    module_names=[df[df.Module_ID==module_id].module.unique().tolist()[0] for module_id in module_ids]
    df[df.Module_ID.isin(module_ids)].module.unique().tolist()
    return module_ids,module_names


def situation_recommendations(df_rslt,module_id,n=3,nan_id=16):
    output_ids=[]
    situation_IDs = df_rslt[df_rslt['module_ID']==int(module_id)]["situation_ID"].unique().tolist()
    print('##########situation_IDs',situation_IDs)
    print(df_rslt[df_rslt.module_ID==int(module_id)]["situation_ID"].unique())
    for i in situation_IDs:
        if i!=nan_id :   
            if len(output_ids)<n:
                output_ids.append(i)

    situation_names=[df[df.Situation_ID==output_id]["Situation "].unique().tolist()[0] for output_id in output_ids]
    # df[df.Situation_ID.isin(output_ids)]["Situation "].unique().tolist()
    print(situation_names)
    print(output_ids)
    return output_ids,situation_names
        

def question_recommendations(df_rslt_with_qst,situation_ID,n=3):
    questions=[]
    if df_rslt_with_qst.head(1)["category"].values[0]=="question" and df_rslt_with_qst.head(1)["similarity"].values[0]> 0.8 :#and df_rslt_with_qst.head(1)["situation_ID"].values[0]==22:

        questions=df_rslt_with_qst.head(1)["ralated_responses"].values.tolist()
    questions.extend(df_rslt_with_qst[df_rslt_with_qst['situation_ID']==situation_ID]["ralated_responses"].values.tolist())
    output=[]
    reste=[]
    question_names=[]
    reste_question=[]
    resp_done=[]
    for i in questions:
        for j in i:
            q_id=random.choice(df[df.response_ID==int(j)]["Question_ID"].unique().tolist())
            if len(output)<n and q_id not in output and j not in resp_done:
                output.append(q_id)
                resp_done.append(j)
                question_names.append(df[df.Question_ID==int(q_id)]["Question AI"].unique().tolist()[0])
            elif len(output)>=n and q_id not in output and q_id not in reste:
                 
                reste.append(q_id)
                reste_question.append(df[df.response_ID==int(j)]["Question AI"].unique().tolist()[0])

    # question_names=df[df.Question_ID.isin(output)]["Question AI"].unique().tolist()
    return(output,question_names,reste,reste_question)

# def question_recommendations1(df_rslt_with_qst,situation_ID,n=3):
#     questions=[]
#     if df_rslt_with_qst.head(1)["category"].values[0]=="question" :#and df_rslt_with_qst.head(1)["situation_ID"].values[0]==22:

#         questions=df_rslt_with_qst.head(1)["ralated_questions"].values.tolist()
#     questions.extend(df_rslt_with_qst[df_rslt_with_qst['situation_ID']==situation_ID]["ralated_questions"].values.tolist())
#     output=[]
#     reste=[]
#     question_names=[]
#     reste_question=[]
#     for i in questions:
#         for q in i:
#             j=random.choice(q)
#             if len(output)<n and j not in output :
#                 output.append(j)
#                 question_names.append(df[df.Question_ID==int(j)]["Question AI"].unique().tolist()[0])
#             elif len(output)>=n and j not in output and j not in reste:
                 
#                 reste.append(j)
#                 reste_question.append(df[df.Question_ID==int(j)]["Question AI"].unique().tolist()[0])

#     # question_names=df[df.Question_ID.isin(output)]["Question AI"].unique().tolist()
#     return(output,question_names,reste,reste_question)
def get_responses(question_id):

    response=df[df.Question_ID==question_id]['Réponse  Quasi-finale'].unique().tolist()
    return(response)
class ActionAskNavigateData(Action):
    def name(self) -> str:
        return "action_ask_navigate_data"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        message = "هل تريد التنقل في البيانات؟"
        buttons = [{"title": "نعم", "payload": "/affirm"}, {"title": "لا", "payload": "/deny"}]

        dispatcher.utter_button_message(message, buttons=buttons)
        return []

class ActionStopNavigation(Action):
    def name(self) -> str:
        return "action_stop_navigation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        dispatcher.utter_message("بالتأكيد! إذا كان لديك أي أسئلة أخرى أو إذا كنت بحاجة إلى مزيد من المعلومات، فلا تتردد في طرحها. أنا هنا للمساعدة")
        return []
    
class ActionGetUserQuestion(Action):
    def name(self) -> str:
        return "action_get_user_question"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> list:

        user_message_all = tracker.latest_message.get('text')
        print('################################MESSAGE',user_message_all)
        sender_id = tracker.sender_id
        path="records/df_recommendations_"+sender_id+".xlsx"
        # Assuming you have a function to provide recommendations based on user input
        df_recommendations = provide_recommendations(  user_message_all ,THRESH=0.3, n=1000,df=df,unique_values_dict=unique_values_dict,BERT_weights=BERT_weights)
        df_recommendations.to_excel(path,index=False)
        if df_recommendations.empty:
            dispatcher.utter_message("من فضلك أعد صياغة سؤالك")
            return []
        else :
             module_ids,module_names=module_recommendations(df_recommendations,n=3)
            #  button_list = [{"title": module_names[i], "payload": '/module_definitions'+str(module_ids[i])} for i in range(len(module_ids))]
             button_list = [{"title": module_names[i],  "payload": f'/inform_module{{"module_id":"{str(module_ids[i])}"}}'} for i in range(len(module_ids))]

             dispatcher.utter_message(text="اختر الوحدة المتعلقة بسؤالك", buttons=button_list)
        # Set the user_question value in a slot for future use
        return [SlotSet("user_question", user_message_all)]


class ActionReselectModule(Action):
    def name(self) -> str:
        return "action_reselect_module"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> list:

        sender_id = tracker.sender_id
        path="records/df_recommendations_"+sender_id+".xlsx"
        # Assuming you have a function to provide recommendations based on user input
        df_recommendations=pd.read_excel(path)
        if df_recommendations.empty:
            dispatcher.utter_message("من فضلك أعد صياغة سؤالك")
            return []
        else :
             module_ids,module_names=module_recommendations(df_recommendations,n=3)
            #  button_list = [{"title": module_names[i], "payload": '/module_definitions'+str(module_ids[i])} for i in range(len(module_ids))]
             button_list = [{"title": module_names[i],"payload": f'/inform_module{{"module_id":"{str(module_ids[i])}"}}'} for i in range(len(module_ids))]

             dispatcher.utter_message(text="اختر الوحدة المتعلقة بسؤالك", buttons=button_list)
        # Set the user_question value in a slot for future use
        return []
    
class ActionGetModuleId(Action):
    def name(self):
        return "action_get_module_id"

    def run(self, dispatcher, tracker, domain):
        # Extract payload from the latest message

        # module_number = tracker.latest_message['text']

        # print('######module_number',module_number)
        # latest_intent = tracker.latest_message.get("intent", {}).get("name", "")
        latest_entities = tracker.latest_message.get("entities", [])

        if latest_entities:
    # Assuming you have only one entity in the latest message
            entity_name = latest_entities[0].get("entity")
            entity_value = latest_entities[0].get("value")
        print('######latest_intent',entity_name,entity_value)

        # Your action logic here
        return [SlotSet(entity_name, entity_value)]


class ActionGet_Situations(Action):
    def name(self):
        return "action_get_situations"

    def run(self, dispatcher, tracker, domain):
        # Access the ID from the slot
        # module_number = tracker.latest_message['text']
        module_number = tracker.get_slot('module_id')
        print('##############SLOT',module_number)
        # dispatcher.utter_message(text=f"You choosed module{module_number}")
        sender_id = tracker.sender_id
        path="records/df_recommendations_"+sender_id+".xlsx"
        df_rslt=pd.read_excel(path)
        situation_ids,situation_names=situation_recommendations(df_rslt,int(module_number),n=3)
        if situation_ids==[]:
                        dispatcher.utter_message("لا يوجد السياق متاح في هذه الوحدة")
        else:

            button_list = [{"title": situation_names[i], "payload": f'/inform_module{{"situation_id":"{str(situation_ids[i])}"}}'  } for i in range(len(situation_ids))]
            button_list.append({"title": "انقر هنا لإعادة إختيار الوحدة", "payload": '/rechoisir_module'})
            dispatcher.utter_message(text= "اختر السياق الأقرب إلى سؤالك",buttons=button_list)
        return []

class ActionGetsituationId(Action):
    def name(self):
        return "action_get_situation_id"

    def run(self, dispatcher, tracker, domain):
        # Extract payload from the latest message

        # situation_number = tracker.latest_message['text']
        # print('######situation_number',situation_number)
        latest_entities = tracker.latest_message.get("entities", [])

        if latest_entities:
    # Assuming you have only one entity in the latest message
            entity_name = latest_entities[0].get("entity")
            entity_value = latest_entities[0].get("value")
        # Your action logic here
        return [SlotSet(entity_name, entity_value)]


class ActionGet_Questions(Action):
    def name(self):
        return "action_get_questions"

    def run(self, dispatcher, tracker, domain):
        # Access the ID from the slot
        # situation_number = tracker.latest_message['text']
        situation_number = tracker.get_slot('situation_id')
        # dispatcher.utter_message(text=f"You choosed situation {situation_number}")

        # Use the ID in your action logic
        sender_id = tracker.sender_id
        path="records/df_recommendations_"+sender_id+".xlsx"
        df_rslt=pd.read_excel(path)      
        # df_with_qst=add_qst_ids(df,df_rslt)
        df_resp=add_resp_ids(df,df_rslt)
        df_with_qst=add_qst_ids(df,df_resp)
        df_with_qst.to_excel(path,index=False)

        question_ids,question_names,reste,reste_question=question_recommendations(df_with_qst,int(situation_number),n=5)
        print(question_ids,question_names)
        if question_ids==[]:
                        dispatcher.utter_message("لا يوجد سؤال متاح في هذا السياق")
        else:
            print("##########reste", len(reste))
            list_prop=[
                "اختر السؤال الأقرب",
                "حدد السؤال الذي يناسبك أكثر",
                "اختر السؤال الأقرب إلى ما تبحث عنه",
                "اختر السؤال الذي يلائم احتياجاتك",
                "اختر الاستفسار الذي يتناسب مع موضوعك",
                "اختر السؤال الأقرب إلى متطلباتك",
                "اختر السؤال الذي يتناسب مع طلبك",
                "اختر الاستفسار الأنسب لك",
                "اختر السؤال الذي يناسب طلبك بشكل أفضل",
                "اختار الاستفسار الذي يعكس اهتماماتك",
                "اختر السؤال الأقرب إلى سؤالك"
                    ]
            random.shuffle(list_prop)

            button_list = [{"title": question_names[i], "payload": f'/inform_module{{"question_id":"{str(question_ids[i])}"}}' } for i in range(len(question_ids))]
            dispatcher.utter_message(text= list_prop[0],buttons=button_list)
        return []
    
class ActionGetQuestionId(Action):
    def name(self):
        return "action_get_question_id"

    def run(self, dispatcher, tracker, domain):
        # Extract payload from the latest message

        # question_number = tracker.latest_message['text']
        # print('######question_number',question_number)
        latest_entities = tracker.latest_message.get("entities", [])

        if latest_entities:
    # Assuming you have only one entity in the latest message
            entity_name = latest_entities[0].get("entity")
            entity_value = latest_entities[0].get("value")
        # Your action logic here
        return [SlotSet(entity_name, entity_value)]
    
class ActionGet_Response(Action):
    def name(self):
        return "action_get_response"

    def run(self, dispatcher, tracker, domain):
        # Access the ID from the slot
        # question_number = tracker.latest_message['text']
        question_number = tracker.get_slot('question_id')
        # dispatcher.utter_message(text=f"You choosed question {question_number}")
        response=get_responses(int(question_number))
        # Use the ID in your action logic
        dispatcher.utter_message(text=f" {response[0]}")
        messages = [
            "إذا كانت لديك استفسارات إضافية، فلا تتردد في طرحها",
            "في حال كانت لديك أي أسئلة إضافية، لا تتردد في السؤال",
            "إذا كنت بحاجة إلى أي استفسار آخر، فأنت حر في طرحه",
            "إذا كان لديك سؤال آخر، فأنا هنا للمساعدة",
            "إذا كان لديك أسئلة أخرى، لا تتردد في طرحها"
                  ]

        # Shuffle the messages randomly
        random.shuffle(messages)

        # Choose and send one of the messages
        response = messages[0]
        dispatcher.utter_message(text=response)

        return []
    
class ActionGuidance(Action):
    def name(self) -> Text:
        return "action_guidance"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = (
            "للحصول على تعاريف الوحدات، اكتب  **تعريف الوحدات**\n"
            "للبحث عن سؤال معين، اكتب **تصفح البيانات**"
        )

        dispatcher.utter_message(text=message, parse_mode="Markdown")

        return []
    

    
class ActionUtterModuleButtons(Action):
    def name(self) -> Text:
        return "action_utter_module_buttons"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Define a list of module titles
        module_titles = [
            "مفاهيم التعرف على الميدان",
            "تحديد أفراد الأسرة",
            "الميزات الديموغرافية لأفراد الأسرة",
            "الخصوبة",
            "الصعوبة في ممارسة الأنشطة الاعتيادية",
            "الهجرة الدولية لأفراد الأسرة خلال السنوات الخمس الأخيرة",
            "أحداث الوفاة ضمن أفراد الأسرة خلال الخمس سنوات الأخيرة",
            "الهجـــرة",
            "الأمية واللغات",
            "التعليم",
            "النشـاط الاقتصادي والتنقل للـعمل",
            "الحماية الاجتماعية",
            "استعمال أجهزة تكنولوجيا المعلومات والاتصالات",
            "ظروف سكن الأسرة",
            "حالات عامة"
            # Add more module titles as needed
        ]

        # Create buttons based on the list of module titles
        button_list = [{"title": title, "payload": f"module_definitions{i+1}"} for i, title in enumerate(module_titles)]

        # # Generate the utterance with buttons
        # message = {
        #     "text": "اضغط على اسم الوحدة للحصول على تعريفها",
        #     "buttons": buttons
        # }

        # dispatcher.utter_message(attachment=message)
            
        dispatcher.utter_message(text= "اضغط على اسم الوحدة للحصول على تعريفها", buttons=button_list)

        return []
    
class ActionGetModuleDefinitions(Action):
    def name(self) -> Text:
        return "action_get_module_definitions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the entire dictionary of definitions
        definitions_dict = {
            "module_definitions1": "المبادئ والمصطلحات الأساسية في مجال الإحصاء السكاني والعمران، بما في ذلك مفاهيم مثل الإحصاء ومنطقة الإحصاء والبناية والمسكن وأنواع البنايات المختلفة والمصطلحات ذات الصلة",
            "module_definitions2": "تحديد بنية الأسرة وعدد أفرادها وتحديد العلاقات بينهم وكذلك توثيق معلومات حول هوياتهم وخصائصهم الديموغرافية",
            "module_definitions3": "توثيق الخصائص الرئيسية لأفراد الأسرة، مثل العمر، والجنس، والحالة الاجتماعية، والجنسية، وأي خصائص أخرى ترتبط بأفراد الأسرة",
            "module_definitions4": "تسجيل عدد الأطفال المولودين للأسرة خلال فترة زمنية معينة، وتحديد معدل الخصوبة في الأسرة",
            "module_definitions5": "تقييم مدى الصعوبة أو السهولة في أداء الأنشطة اليومية لأفراد الأسرة ، مثل الحركة، والعناية الذاتية، وغيرها",
            "module_definitions6": "تسجيل حركة الهجرة الدولية لأفراد الأسرة، بما في ذلك الهجرة إلى ومن البلاد",
            "module_definitions7": "تسجيل وتوثيق الحوادث المتعلقة بالوفيات في دائرة أفراد الأسرة خلال الفترة المحددة",
            "module_definitions8": "رصد وتوثيق حركة التنقل للأفراد بين المناطق الجغرافية داخل البلاد",
            "module_definitions9": "تحديد مستوى الأمية واللغات التي يجيدونها أفراد الأسرة",
            "module_definitions10": "توثيق مستوى التعليم والتحصيل الدراسي لكل فرد في الأسرة",
            "module_definitions11": "تحديد مصدر العيش والنشاط الاقتصادي الرئيسي لأفراد الأسرة وطريقة التنقل إلى مكان العمل",
            "module_definitions12": "توثيق استفادة أفراد الأسرة من برامج الحماية الاجتماعية والضمان الاجتماعي",
            "module_definitions13": "تقييم وتوثيق استخدام أفراد الأسرة للتكنولوجيا الحديثة مثل الإنترنت والهواتف الذكية",
            "module_definitions14": "توثيق معلومات حول سكن الأسرة بما في ذلك نوع الإقامة والحالة الصحية للمسكن ومرافقه",
            "module_definitions15":"حالات عامة"
            # Add more definitions as needed
        }

        user_selection = tracker.latest_message.get('text')

        # Send the entire dictionary as a response
        dispatcher.utter_message(text=str(definitions_dict[user_selection]))

        return []
    
class ActionGetModuleDefinitions2(Action):
    def name(self) -> Text:
        return "action_get_module_definitions2"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the entire dictionary of definitions
        definitions_dict={
 'module_definitions1': 'المبادئ والمصطلحات الأساسية في مجال الإحصاء السكاني '
                        'والعمران، بما في ذلك مفاهيم مثل الإحصاء ومنطقة '
                        'الإحصاء والبناية والمسكن وأنواع البنايات المختلفة '
                        'والمصطلحات ذات الصلة',
 'module_definitions10': 'يهدف محور التعليم في الاستمارة إلى تحديد استفادة '
                         'أفراد الأسر من التعليم بمختلف مستوياته، وذلك من خلال '
                         'الاستفسار عن عدة نقط. بدءًا بالاستفادة من التعليم '
                         'الأولي، المستوى التعليمي العام ونوعه، الدراسة خلال '
                         'السنة الدراسية 2023-2024، ثم أعلى دبلوم أو شهادة '
                         'محصل عليها في التعليم العام والتكوين المهني.',
 'module_definitions11': 'في محور النشاط الاقتصادي والتنقل للعمل، تمت برمجة '
                         'عدة أسئلة تمكن من تصنيف السكان الإعتياديين حسب نوع '
                         'نشاطهم الاقتصادي وتجميع بيانات حول المهن والتنقل '
                         'للعمل. يتم ذلك عبر الاستفسارا عن نوع النشاط '
                         'الاقتصادي، تحديد المهنة والحالة في المهنة والنشاط '
                         'الرئيسي للمؤسسة، ثم تحديد مكان العمل ووسيلة التنقل '
                         'المستعملة. هذه البيانات ستُمكن من توفير قاعدة بيانات '
                         'مهمة لتقييم البرامج الاجتماعية والاقتصادية وكذا وضع '
                         'استراتيجيات مستقبلية لتحقيق الأهداف المسطرة سواء '
                         'فيما يتعلف بأهداف التنمية المستدامة لسنة 2030 أو '
                         'أهداف النموذج التنموي الجديد في أفق سنة 2035',
 'module_definitions12': 'في سياق تعميم الحماية الاجتماعية، سيتم تجميع '
                         'البيانات المتعلقة بهذا الموضوع ليتم رص التقدم '
                         'المُحرز في هذا المجال. في الجزء الأول، سيتم '
                         'الاستفسار عن الانخراط أو الاستفادة من أنظمة التغطية '
                         'الصحية (AMO، AMO تضامن، شركة تأمين خاصة، مؤسسة أخرى '
                         'للتضامن). وفي الجزء الثاني، سيتم تجميع المعطيات حول '
                         'الإنخراط أو الاستفادة من إحدى أنظمة التقاعد المغربية '
                         '( CMR، CNSS، RCAR، CIMR)',
 'module_definitions13': 'يهتم محور استعمال تكنولوجيا المعلومات والاتصالات إلى '
                         'تحديد مدى توفر الأفراد البالغين 5 سنوات فأكثر على '
                         'هاتف نقال خاص ذكي أو عادي، جهاز كمبيوتر مكتبي خاص أو '
                         'كمبيوتر محمول خاص أو لوحة إلكترونية خاصة، وكذلك مدى '
                         'استعمالهم للأنترنيت خلال الثلاث أشهر الأخيرة. كل هذه '
                         'المعطيات الإحصائية ستمكن من تقييم مستوى المؤِشرات '
                         'المرتبطة بأهداف التنمية المستدامة لسنة 2030.',
 'module_definitions14': 'من أجل تحديد الظروف السكنية لكل أسرة تمت برمجت سلسلة '
                         'من الأسئلة حول خاصيات المسكن وكيفية استعمال بعض '
                         'تجهيزاته. هذه البيانات تساع بشكل كبير في تقدير '
                         'احتياجات الإسكان والنجاح في التخطيط لبرامج الإسكان. '
                         'يُذكر بأن تعريف المسكن في الإحصاء هو المكان الذي '
                         'تعيش فيه الأسرة، ويمكن أن يكون عبارة عن حجرة واحدة '
                         'أو عدة حجرات مخصصة للسكن، والمسكن يتوفر على مدخل أو '
                         'عدة مداخل مباشرة. يتم الاستفسار في هذا المحور حول '
                         'خصائص هذا المسكن، وتوفر الأسرة على بعض التجهيزات '
                         'الأساسية، وكذا المسافة التي تفصل المسكن على بعض '
                         'المرافق والتجهيزات الأساسية ومعطيات أخرى تصف ظروف '
                         'سكن الأسرة.',
 'module_definitions15': 'تهدف الأسئلة والأجوبة حول الحالات العامة لتأطير تصرف '
                         'الباحث أثناء تعامل مع مختلف الأسر، سواءً كان ذلك في '
                         'ارتباط مباشر مع ملأ الإستمارة، أو كان عاماً مثل '
                         'الحصول على دعوة لشرب الشاي مع أفراد الأسرة وغيرها. '
                         'وهذا ليتم تأطير الأفعال قانونيا وأخلاقيا، وكذا تسهيل '
                         'عملية الاستجواب وملأ الإستمارة.',
 'module_definitions2': 'تهدف فقرة تحديد أفراد الأسرة إلى تعداد السكان '
                        'المقيمين الإعتياديين ضمن الأسر القاطنة بكل منطقة '
                        'إحصاء. بحيث أن الأسرة بمفهوم الإحصاء هي مجموعة من '
                        'الأشخاص يقيمون بصفة إعتيادية بمسكن واحد أو جزء منه، '
                        'وتكون لهم نفقات مشتركة. والمقيم الإعتيادي هو كل فرد '
                        'أسرة يقيم بالمسكن أو له نية الإقامة به لمدة لا تقل عن '
                        '6 أشهر.',
 'module_definitions3': 'الغرض من تحديد المميزات الديموغرافية لأفراد الأسرة هو '
                        'معرفة مميزات السكان الإعتياديين وتركيبتهم. السن '
                        'والجنس من أكثر الخاصيات التي تتم جدولة معلوماتها بصفة '
                        'مترابطة مع المعطيات الأخرى المُجَمعة في باقي أجزاء '
                        'الإستمارة. تساعد هذه البيانات في تحليل تطور المميزات '
                        'الديموغرافية في الزمن. يتم أيضا تجميع البيانات عن '
                        'الجنسية، التسجيل في دفتر الحالة المدنية، الحالة '
                        'الزواجية والسن عند الزواج الأول.',
 'module_definitions4': 'يهدف إدراج الأسئلة حول الخصوبة وجمع البيانات إلى '
                        'دراسة ظاهرة الخصوبة ووفيات الرضع والأطفال، والحصول '
                        'على معلومات دقيقة للتخطيط واتخاذ القرارات الصحية '
                        'والاجتماعية. يجب التنويه إلى أن جميع الأسئلة حول '
                        'الخصوبة تهم المواليد الأحياء (المواليد الذين ظهرت '
                        'عليهم بعد الولادة علامات الحياة كالتنفس والصراخ أو '
                        'دقات القلب) وليس المواليد الأموات (المواليد الذين لم '
                        'تظهر عليهم علامات الحياة بعد الولادة). وتنقسم الخصوبة '
                        'إلى خصوبة إجمالية أي طيلة الحياة، وإلى خصوبة حالية أي '
                        'خلال 12 شهرًا الأخيرة للنساء في سن الإنجاب فقط، ما '
                        'بين 15 و49 سنة.',
 'module_definitions5': 'بهدف الإحاطة بالصعوبات التي يواجهها الأفراد في القيام '
                        'بالأنشطة اليومية، يتم الاستفسار عن درجة الصعوبة التي '
                        'يواجهها الأفراد بخصوص 6 وظائف أساسية: الرؤية (حتى مع '
                        'استعمال نظارات طبية)، السمع (حتى مع استعمال وسائل '
                        'سمعية)، الحركة (المشي أو صعود الدرج)، التواصل مع '
                        'الآخرين، التذكر والتركيز، والاعتناء بالذات (مثل '
                        'الاستحمام وارتداء الملابس). يتم الاستفسار عن درجة '
                        'الصعوبات المنبثقة عن المشاكل الصحية التي قد تواجه '
                        'الفرد عند قيامه بأنشطة معينة، بدلاً من الاستفسار '
                        'مباشرة عما إذا كان لديه إعاقة معينة.',
 'module_definitions6': 'في محور الهجرة الدولية لأفراد الأسرة خلال السنوات '
                        'الخمس الأخيرة، يتم تجميع المعطيات الخاصة بكل شخص كان '
                        'ضمن أفراد الأسرة وهاجر إلى خارج المغرب في الفترة ما '
                        'بين 1 شتنبر 2019 و 31 غشت 2024. هذه المعطيات تشمل اسم '
                        'الفرد المهاجر، تاريخ الهجرة الأخيرة، جنس وجنسية وسن '
                        'الفرد المهاجر، ثم الخاصيات المتعلقة بالتعليم للفرد عن '
                        'هجرته، ثم سبب هجرته و بلد الإستقبال عند هجرته الأخيرة',
 'module_definitions7': 'يهتم محول أحداث الوفاة ضمن أفراد الأسرة خلال الخمس '
                        'سنوات الأخيرة بتحديد جميع أحداث الوفاة التي وقعت ما '
                        'بين 1 شتنبر 2019 و 31 غشت 2024، ضمن الأفراد الذين '
                        'كانوا يقيمون بصفة إعتيادية مع الأسرة، وذلك سواءً كانو '
                        'رضعا أو أطفالا أو بالغين وكيفما كان جنسهم. سيتم تجميع '
                        'البيانات التي تتمثل في اسم الفرد المتوفي، تاريخ أو '
                        'سنة الوفاة، جنسه، سنه عند الوفاة، حالته الزوجية عند '
                        'الوفاة، ثم أخيرا سبب الوفاة.',
 'module_definitions8': 'الأسئلة المتعلقة بظاهرة الهجرة في الاستبيان تهدف إلى '
                        'دراسة حركة الهجرة بين مختلف الوحدات الإدارية داخل '
                        'المغرب و الحركة السكانية ما بين المغرب والبلدان '
                        'الأخرى. ويتم ذلك عبر الاستفسار عن مكان ازدياد '
                        'الأفراد، مكان إقامتهم ما قبل الحالية، مكان الإقامة '
                        'ليلة بداية الحجر الصحي وعن ما إذا كان الفرد سبق له أن '
                        'أقام بخارج المغرب وسبب القدوم أو العودة في تلك '
                        'الحالة.',
 'module_definitions9': 'محور الأمية واللغات يتطرق إلى 3 أجزاء. أولها الأمية، '
                        'التي تهدف أسئلتها إلى تحديد مدى قدرة الأفراد البالغين '
                        '10 سنوات فأكثر على القراءة والكتابة وكذلك على القيام '
                        'بعمليات حسابية ذهنية أثناء قيامهم بأنشطتهم اليومية. '
                        'ثانيها اللغات المقروءة والمكتوبة، بحيث يهدف هذا الجزء '
                        'إلى تحديد اللغات التي يتمكن الأفراد من القراءة '
                        'والكتابة بها حسب درجة الإتقان. وآخرها اللغات المحلية '
                        'المستعملة، بحيث يتم استفسار الأفراد عن أي لغة محلية '
                        'أكثر استعمالا في تعاملاتهم اليومية.'}

        user_selection = tracker.latest_message.get('text')

        # Send the entire dictionary as a response
        dispatcher.utter_message(text=str(definitions_dict[user_selection]))

        return []

    
class LogConversation(Action):
    def name(self) -> Text:
        return "action_log_conversation"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Extract conversation data with message types and sender IDs
        sender_id = tracker.sender_id
        conversation_data = []

        for event in tracker.events:
            if 'text' in event:
                message = event['text']
                message_type = 'user' if event['event'] == "user" else 'bot'
                time = event.get('timestamp', '')
                conversation_data.append({'sender_id': sender_id, 'message': message, 'message_type': message_type, 'Time': time})

        # Format the date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Specify the file path
        file_path = "conversation_log.txt"

        # Open the file in append mode and write the formatted datetime and conversation data
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"Timestamp: {current_datetime}\n")
            for entry in conversation_data:
                # file.write(f"(sender_id: {entry['sender_id']}){entry['message_type'].capitalize()}: {entry['message']} (Time: {entry['Time']})\n")
                file.write(f"sender_id: {entry['sender_id']} , {entry['message_type'].capitalize()}: {entry['message']} , Time: {entry['Time']}\n")

            file.write("\n")  # Add a newline between conversations

        return []
    

    
