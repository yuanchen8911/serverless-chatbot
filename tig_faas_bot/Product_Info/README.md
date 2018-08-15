# Product Information 

This repo is related with `Running Guide` `Part2.6`.

This directory is a collection of the product info used in the FaaS-Shopping-Bot.

The product name came from [Instacart](https://www.instacart.com/datasets/grocery-shopping-2017). For the demo purpose, we built a small proof-of-concept (POC) dataset. The POC dataset contains 16 products. There are: 

- 7 Juice
- 3 Sausage
- 3 Tea
- 2 Milk
- 1 Cookie

## File Tree

```
Product_Info/
├── product_info_list.csv
├── product_name_and_synonym.csv
├── product_name_and_synonym_entity_set.csv
├── README.md
└── entity_product_name_map.csv.csv

0 directories, 5 files
```

## File Introduction

**product_info_list.csv**

Each line represents a product. The first column is the name of the product. And the second column is the price of the product.

**product_name_and_synonym.csv**

One product per line. The first column is the product name. And all remaining columns are corresponding synonyms.

**product_name_and_synonym_entity_set.csv**

One [entity](https://dialogflow.com/docs/entities) per line. The entity is used for Natural Language understanding (NLU) modules like [Dialogflow](https://dialogflow.com/) to extract parameter values. This entity set contains all the product name and corresponding synonyms. 

**entity_product_name_map.csv**

One entity per line. This first column is the entity value. And the remaining columns are all corresponding possible product name. 