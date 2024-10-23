from .models import Project
from .serializers import WebLinkSerializer, QuerySerializer, ProjectsSerializer, FileUploadSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.contrib.auth import get_user_model
import os
from rest_framework.views import APIView
from langchain import OpenAI, VectorDBQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from django.core.cache import cache
from .utils import scrap_website, changeJson, scrap_pdf
from rest_framework.permissions import IsAuthenticated
from langchain import PromptTemplate
from langchain.embeddings.openai import OpenAIEmbeddings


User = get_user_model()
os.environ['OPENAI_API_KEY'] = ''
davinci = OpenAI(model_name="gpt-3.5-turbo-0613")

class WebLinkView(generics.GenericAPIView):
    serializer_class = WebLinkSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            web_link = serializer.data['link']
            project_name = serializer.data['project_name']
            url = scrap_website(web_link,project_name)

            Project.objects.create(owner= request.user, project_name=project_name, project_content=url)
            ProjectView().invalidate_cache()
            serializer.data['response_content'] = url
            return Response(serializer.data, status= status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)




class QueryView(generics.GenericAPIView):
    serializer_class = QuerySerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        serializer = self.serializer_class(data= data)

        if serializer.is_valid():

            project_name = serializer.data['project_name']
            query = serializer.data['query_data']
            project = Project.objects.get(project_name=project_name)

            prompt = """
            Answer the question based on the context below. If the question cannot be answered using the information provided ansswer with "Based on the context of this information I don't know the answer"

            Context: {context}

            Question: {query}

            Answer: """

            prompt_template = PromptTemplate(
                input_variables=["query", "context"],
                template=prompt
            )

            if "value" in request.session and 'project_name' in request.session:
                if project_name == request.session['project_name']:

                    texts = request.session['value']
                    embeddings = OpenAIEmbeddings()

                    vectorstore = FAISS.from_texts(texts, embeddings)
                    similarity = vectorstore.similarity_search(query, 5)
                    context = ''
                    for i in range(len(similarity)):
                        context = context + similarity[i].page_content
                        print(similarity[i].page_content)
                        print("------------------------------------")

                    message = davinci(prompt_template.format(
                        query=query,
                        context=context))

                    return Response({'message': message}, status=status.HTTP_200_OK)
                else:
                    url = project.project_content
                    texts = changeJson(url)

                    request.session['value'] = texts
                    request.session['project_name'] = project_name
                    embeddings = OpenAIEmbeddings()
                    vectorstore = FAISS.from_texts(texts, embeddings)
                    similarity = vectorstore.similarity_search(query, 5)
                    context = ''
                    for i in range(len(similarity)):
                        context = context + similarity[i].page_content

                    message = davinci(prompt_template.format(
                        query=query,
                        context=context))
                    return Response({'message': message}, status=status.HTTP_200_OK)
            else:

                url = project.project_content
                texts = changeJson(url)

                request.session['value'] = texts
                request.session['project_name'] = project_name
                embeddings = OpenAIEmbeddings()

                vectorstore = FAISS.from_texts(texts, embeddings)

                similarity = vectorstore.similarity_search(query, 5)

                context =''
                for i in range(len(similarity)):
                    context = context + similarity[i].page_content


                message = davinci(prompt_template.format(
                    query=query,
                    context=context))
                return Response({'message': message}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)




class ProjectView(APIView):
    permission_classes = (IsAuthenticated,)
    cache_timeout = 3600
    cache_version = 1
    key = ''

    def get(self, request):
        cache_key = f"product_data_v{self.cache_version}_{request.user.id}"
        cached_data = cache.get(cache_key)
        self.key = cache_key
        if cached_data:

            return Response(cached_data, status= status.HTTP_200_OK)
        else:
            queryset = Project.objects.select_related().filter(owner= request.user)
            serializer = ProjectsSerializer(queryset, many=True)
            cache.set(cache_key, serializer.data, timeout=self.cache_timeout)
            return Response(serializer.data, status= status.HTTP_200_OK)


    def invalidate_cache(self):
        cache.clear()



class FileView(generics.GenericAPIView):
    serializer_class = FileUploadSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            pdf_file = serializer.validated_data['file']
            project_name = serializer.data['project_name']
            url = scrap_pdf(pdf_file, project_name)
            Project.objects.create(owner=request.user, project_name=project_name, project_content=url)
            ProjectView().invalidate_cache()
            serializer.data['response_content'] = url
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
