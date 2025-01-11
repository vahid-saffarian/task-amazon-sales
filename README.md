## Thank you in advance for taking the time to review this submission!

### Some notes on the provided data and my implementation:
* A dozen of the rows had misplaced columns. The values were shifted one column to the right, resulting in data inconsistency. They were detected and manually modified.
* About 1500 Image links had misconstructed urls leading to 404 errors. The issue seems to arise from Amazon’s image rendering mechanism which adds the below parameters to the url. The redundant part of the urls were removed making the broken image links work. The patterns were as follows:
  - /images/W/IMAGERENDERING_521856-T1
  - /images/W/IMAGERENDERING_521856-T2
* Some rows had null values for ratings and no_of_ratings. They were left unhandled, but it could be suggested for them to be filled with an average value, or crawled again.
* The links to Amazon pages include a `ref` parameter which is used to identify where the user is coming from, e.g. search, category pages, etc. and is irrelevant to the product itself. I found out that there are several links that refer to the same page but because of different refs, aren’t considered unique with the product. To address this matter, I tried making a new column of raw links i.e. ‘unique_link’, removing the unnecessary parameters, but I decided to keep working with the links column. More on that in the next note.
* Each row of the data represents a sales record. According to the requirements of the task, the identifier of sales records of a product is its name; However, I came across the issue that rows with the same name, don’t necessarily have the same link, or image, or price, or even sub category. It was ASSUMED that products with the same name could be posted on Amazon by different vendors, so they may have different values for aforementioned parameters despite being the same product. So the generic attributes of the sales report for a product (all the columns except date, such as ratings, price, link, etc.) are fetched from the first instance of the product in the data and don’t correspond to all of the product’s sales records, while the number of sales in different dates are accumulated for the product.
* The maximum number of sales for a single product is 4, meaning the most populated charts will only have 4 instances. In order to get a better insight from such data, a few solutions could be recommended, such as grouping products together based on category or additional differentiating parameters. Sale stats are as follows:
  - Products with 4 sales: 2
  - Products with 3 sales: 25
  - Products with 2 sales: 389
  - Products with 1 sale: 4425
* Not all the names of the products were complete. Many of them ended with three dots at character limit, leaving out the rest of the name. For the sake of better UX, It could be recommended to crawl the links and get the full name of the products using tools such as Beautiful Soup or Selenium.


### Some prompts and search queries used throughout the implementation:

* I have a project. I will give you its requirements and I want you to ask me questions to get enough information so that you can give me a mind map and suggestions on the architecture of it.
The project is to design and implement plotting the daily sales trend of Amazon products.
For backend and frontend I must use dash-plotly.
Plots must contain a dropdown filter of products name that is fetched from backend.
I must use Redis or RabbitMQ to store values based on the filtered product.
All main functionalities must be handled with Celery.
The whole code-base must be in python.Things that matter in implementation:
  - frontend design
  - taking OOP and Functionality into account
  - clean coding
  - problem-solving approach

* I want you to remember this project as "Task Project" so you can also answer my future questions about it.

* dash-plotly doc

* how to start the celery worker automatically in python

* when I run this
celery -A backend beat --loglevel=info
I get this error
_gdbm.error: [Errno 11] Resource temporarily unavailable: 'celerybeat-schedule'

* how to validate '1,234' as int

* how many rows have unique name and date in df?

* what is the most efficient way to save a list of dates on redis?

* If I iterate over all the dates stored on redis to convert them to datetime, it will be inefficient as time accumulates
How to solve it?

