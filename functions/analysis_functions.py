import ccxt.async_support as ccxt
import pandas as pd
import talib
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import yfinance as yf
from tavily import TavilyClient
import asyncio

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
exchange = ccxt.binance()
tavilyClient = TavilyClient(TAVILY_API_KEY)


class analysisModel(BaseModel):
    recommendation: str = Field(..., description="One of BUY, SELL, or HOLD")
    justification: str = Field(...,
                               description="Concise explanation of the analysis")


async def quantitative_analysis(coin: str):
    try:
        bars = await exchange.fetch_ohlcv(
            f'{coin}/USDT', timeframe='1d', limit=180)
    except Exception as e:
        return 404, "Unable to find the requested coin"

    df = pd.DataFrame(
        bars, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df.set_index('Timestamp', inplace=True)

    df['SMA20'] = talib.SMA(df['Close'], timeperiod=20)
    df['SMA50'] = talib.SMA(df['Close'], timeperiod=50)
    df['RSI'] = talib.RSI(df['Close'], timeperiod=14)

    upper_band, middle_band, lower_band = talib.BBANDS(
        df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['BB_upper'] = upper_band
    df['BB_middle'] = middle_band
    df['BB_lower'] = lower_band

    macd, macd_signal, macd_hist = talib.MACD(
        df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['MACD'] = macd
    df['MACD_signal'] = macd_signal
    df['MACD_hist'] = macd_hist

    obv = talib.OBV(df['Close'], df['Volume'])
    df['OBV'] = obv

    dataframe_context = df.tail(10).to_markdown()

    prompt_template = ChatPromptTemplate.from_template(
        """
        You are a senior financial analyst specializing in cryptocurrency markets. You will receive a summary context of a crypto asset's recent price and indicator data presented in a Pandas DataFrame. The DataFrame includes the following columns for the most recent data points: Open, High, Low, Close, Volume, RSI, Bollinger Bands (upper, middle, lower), SMA for 20-day and 50-day, MACD, MACD signal, and MACD histogram.

        Analyze this data carefully to perform the following:

        1. Identify if a "Golden Cross" has occurred recently (20-day SMA crossing above 50-day SMA), or a "Death Cross" (20-day SMA crossing below 50-day SMA).
        2. Interpret the RSI value:
        - RSI > 70 suggests the crypto asset is overbought (potential reversal or sell signal).
        - RSI < 30 suggests the crypto asset is oversold (potential rebound or buy signal).
        3. Examine the position of the Close price relative to the Bollinger Bands:
        - Close price near or above upper band may indicate overbought conditions.
        - Close price near or below lower band may indicate oversold conditions.
        4. Analyze MACD and signal line crossovers:
        - MACD crossing above signal line indicates bullish momentum.
        - MACD crossing below signal line indicates bearish momentum.
        5. Consider volume-based insights from On-Balance Volume if available to confirm buying or selling pressure.

        Keep in mind that cryptocurrency markets are highly volatile and trade 24/7, which may affect indicator sensitivity and signal strength.

        Based on the above, provide your **final recommendation**: BUY, SELL, or HOLD.

        Also provide a **concise justification paragraph** explaining how each indicator influenced your decision. Reference insights from the SMA crossover, RSI, Bollinger Bands, MACD, and volume if applicable. Mention the numeric values **always**.

        Return the result in JSON format with keys "recommendation" and "justification" only.

        ---

        Here is the crypto data context as a table for your reference:

        {dataframe_context}

        Please generate a clear, expert recommendation with reasoning based on this information.
        """
    )

    prompt = prompt_template.format_prompt(dataframe_context=dataframe_context)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro", api_key=GEMINI_API_KEY, temperature=0)
    output_parser = PydanticOutputParser(
        pydantic_object=analysisModel)
    prompt_text = prompt.to_string()

    analysis_chain = llm | output_parser
    result = await analysis_chain.ainvoke(prompt_text)
    print(result.model_dump())
    return 200, result.model_dump()


async def qualitative_analysis(coin: str):
    try:
        news = yf.Search(f"{coin.upper()}-USD").news
        print(news)
        news_urls = [news_item['link'] for news_item in news]
        if (len(news_urls) == 0):
            raise Exception()
        news_data = "\n".join([result["raw_content"]
                               for result in tavilyClient.extract(news_urls)["results"]])
    except Exception as e:
        return 404, "Unable to find the requested coin"
    prompt_template = ChatPromptTemplate.from_template("""
        You are a senior financial analyst specializing in cryptocurrency markets. Given the following qualitative news article content about cryptocurrency markets, analyze the data and provide a clear trading recommendation.

        Input data (news article content):
        {news_data}

        Your task:
        - Carefully assess the qualitative information including market sentiment, whale activity, price levels, institutional behavior, and macro factors.
        - Based on your assessment, give a clear recommendation of BUY, SELL, or HOLD.
        - Also provide a concise justification for your recommendation, highlighting key points from the news.

        Return the output strictly as a JSON object conforming to this Pydantic model schema:

        {{
            "recommendation": "<BUY|SELL|HOLD>",
            "justification": "<concise explanation summarizing key reasons>"
        }}

        Ensure the JSON output is valid and directly parsable.

        Begin your analysis now.
    """)
    prompt = prompt_template.format_prompt(news_data=news_data)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro", api_key=GEMINI_API_KEY, temperature=0)
    output_parser = PydanticOutputParser(
        pydantic_object=analysisModel)
    prompt_text = prompt.to_string()

    analysis_chain = llm | output_parser
    result = await analysis_chain.ainvoke(prompt_text)
    print(result.model_dump())
    return 200, result.model_dump()


async def integrated_analysis(coin: str):
    try:
        quant_task = quantitative_analysis(coin)
        quali_task = qualitative_analysis(coin)
        status_results = await asyncio.gather(quant_task, quali_task)
        
        (status_quant, quant_recommendation), (status_quali, quali_recommendation) = status_results

        if status_quant == 404 or status_quali == 404:
            return 404, "Unable to find the requested coin."
        
    except Exception as e:
        return 500, "Error during integrated analysis."
    
    prompt_template = ChatPromptTemplate.from_template("""
    You are a senior financial analyst specialized in cryptocurrency markets. I will provide you with two inputs:
    Quantitative analysis results (e.g., price trends, volume, volatility metrics, on-chain data)
    Qualitative analysis results (e.g., market sentiment, regulatory news, technological updates, community feedback)

    Input data:
    Quantitative recommendation: {quant_recommendation}
    Qualitative recommendation: {quali_recommendation}

    Your task:
    - Using your expertise, integrate both quantitative and qualitative insights carefully to produce a clear, well-reasoned recommendation on whether to buy, sell, or hold this cryptocurrency at this time. Please emphasize risks, market conditions, and potential catalysts in your final trading decision."                             
    - Based on your assessment, give a clear recommendation of BUY, SELL, or HOLD.
    - Also provide a concise justification for your recommendation, highlighting key points from the news.

    Return the output strictly as a JSON object conforming to this Pydantic model schema:

    {{
        "recommendation": "<BUY|SELL|HOLD>",
        "justification": "<concise explanation summarizing key reasons>"
    }}

    Ensure the JSON output is valid and directly parsable.

    Begin your analysis now.
    """)
    prompt = prompt_template.format_prompt(
        quant_recommendation=quant_recommendation, quali_recommendation=quali_recommendation)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro", api_key=GEMINI_API_KEY, temperature=0)
    output_parser = PydanticOutputParser(
        pydantic_object=analysisModel)
    prompt_text = prompt.to_string()

    analysis_chain = llm | output_parser
    result = await analysis_chain.ainvoke(prompt_text)
    print(result.model_dump())
    return 200, result.model_dump()
