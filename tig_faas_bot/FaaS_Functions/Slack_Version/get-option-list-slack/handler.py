import os
import sys
import json
import logging

ENTITY_PRODUCT_NAME_MAP = '{"Peach Mango Juice":["Peach Mango Juice"],"peach mango juice":["Peach Mango Juice"],"peach juice":["Peach Mango Juice"],"mango juice":["Peach Mango Juice"],"juice":["Peach Mango Juice","Apple Sparkling Juice Beverage","Organic Pasteurized Apple Juice","All Natural 100% Apple Juice","Pineapple Orange Juice","Organic Orange Juice Concentrate","Organic Orange Turmeric Juice"],"Apple Sparkling Juice Beverage":["Apple Sparkling Juice Beverage"],"apple sparkling juice beverage":["Apple Sparkling Juice Beverage"],"sparkling juice beverage":["Apple Sparkling Juice Beverage"],"apple juice beverage":["Apple Sparkling Juice Beverage"],"apple sparkling beverage":["Apple Sparkling Juice Beverage"],"apple sparkling juice":["Apple Sparkling Juice Beverage"],"apple juice":["Apple Sparkling Juice Beverage","Organic Pasteurized Apple Juice","All Natural 100% Apple Juice"],"apple beverage":["Apple Sparkling Juice Beverage"],"sparkling juice":["Apple Sparkling Juice Beverage"],"sparkling beverage":["Apple Sparkling Juice Beverage"],"juice beverage":["Apple Sparkling Juice Beverage"],"beverage":["Apple Sparkling Juice Beverage"],"Organic Pasteurized Apple Juice":["Organic Pasteurized Apple Juice"],"organic pasteurized apple juice":["Organic Pasteurized Apple Juice"],"pasteurized apple juice":["Organic Pasteurized Apple Juice"],"organic apple juice":["Organic Pasteurized Apple Juice"],"organic pasteurized juice":["Organic Pasteurized Apple Juice"],"organic juice":["Organic Pasteurized Apple Juice","Organic Orange Juice Concentrate","Organic Orange Turmeric Juice"],"pasteurized juice":["Organic Pasteurized Apple Juice"],"All Natural 100% Apple Juice":["All Natural 100% Apple Juice"],"all natural 100% apple juice":["All Natural 100% Apple Juice"],"all natural apple juice":["All Natural 100% Apple Juice"],"natural apple juice":["All Natural 100% Apple Juice"],"natural juice":["All Natural 100% Apple Juice"],"Pineapple Orange Juice":["Pineapple Orange Juice"],"pineapple orange juice":["Pineapple Orange Juice"],"pineapple juice":["Pineapple Orange Juice"],"orange juice":["Pineapple Orange Juice","Organic Orange Juice Concentrate","Organic Orange Turmeric Juice"],"Organic Orange Juice Concentrate":["Organic Orange Juice Concentrate"],"organic orange juice concentrate":["Organic Orange Juice Concentrate"],"organic juice concentrate":["Organic Orange Juice Concentrate"],"organic orange concentrate":["Organic Orange Juice Concentrate"],"orange juice concentrate":["Organic Orange Juice Concentrate"],"organic orange juice":["Organic Orange Juice Concentrate","Organic Orange Turmeric Juice"],"organic concentrate":["Organic Orange Juice Concentrate"],"orange concentrate":["Organic Orange Juice Concentrate"],"juice concentrate":["Organic Orange Juice Concentrate"],"concentrate":["Organic Orange Juice Concentrate"],"Organic Orange Turmeric Juice":["Organic Orange Turmeric Juice"],"organic orange turmeric juice":["Organic Orange Turmeric Juice"],"organic turmeric juice":["Organic Orange Turmeric Juice"],"orange turmeric juice":["Organic Orange Turmeric Juice"],"turmeric juice":["Organic Orange Turmeric Juice"],"Original Pork Sausage":["Original Pork Sausage"],"original pork sausage":["Original Pork Sausage"],"original sausage":["Original Pork Sausage"],"pork sausage":["Original Pork Sausage"],"sausage":["Original Pork Sausage","Smoked Polish Sausage","Smoked Turkey Rope Sausage"],"Smoked Polish Sausage":["Smoked Polish Sausage"],"smoked polish sausage":["Smoked Polish Sausage"],"smoked sausage":["Smoked Polish Sausage","Smoked Turkey Rope Sausage"],"polish sausage":["Smoked Polish Sausage"],"Smoked Turkey Rope Sausage":["Smoked Turkey Rope Sausage"],"smoked turkey rope sausage":["Smoked Turkey Rope Sausage"],"smoked rope sausage":["Smoked Turkey Rope Sausage"],"turkey rope sausage":["Smoked Turkey Rope Sausage"],"smoked turkey sausage":["Smoked Turkey Rope Sausage"],"turkey sausage":["Smoked Turkey Rope Sausage"],"rope sausage":["Smoked Turkey Rope Sausage"],"Organic Breakfast Blend Black Tea":["Organic Breakfast Blend Black Tea"],"organic breakfast blend black tea":["Organic Breakfast Blend Black Tea"],"organic black tea":["Organic Breakfast Blend Black Tea","Organic Earl Grey Black Tea"],"breakfast blend black tea":["Organic Breakfast Blend Black Tea"],"breakfast black tea":["Organic Breakfast Blend Black Tea"],"blend black tea":["Organic Breakfast Blend Black Tea"],"breakfast tea":["Organic Breakfast Blend Black Tea"],"blend tea":["Organic Breakfast Blend Black Tea"],"black tea":["Organic Breakfast Blend Black Tea","Organic Earl Grey Black Tea"],"tea":["Organic Breakfast Blend Black Tea","Organic Earl Grey Black Tea","Sencha Shot Japanese Green Tea"],"Organic Earl Grey Black Tea":["Organic Earl Grey Black Tea"],"organic earl grey black Tea":["Organic Earl Grey Black Tea"],"earl grey black tea":["Organic Earl Grey Black Tea"],"Sencha Shot Japanese Green Tea":["Sencha Shot Japanese Green Tea"],"sencha shot japanese green tea":["Sencha Shot Japanese Green Tea"],"sencha japanese green tea":["Sencha Shot Japanese Green Tea"],"sencha japan green tea":["Sencha Shot Japanese Green Tea"],"sencha green tea":["Sencha Shot Japanese Green Tea"],"japanese green tea":["Sencha Shot Japanese Green Tea"],"japan green tea":["Sencha Shot Japanese Green Tea"],"green tea":["Sencha Shot Japanese Green Tea"],"2% Milkfat Reduced Fat Milk":["2% Milkfat Reduced Fat Milk"],"2% milkfat reduced fat milk":["2% Milkfat Reduced Fat Milk"],"2% reduced fat milk":["2% Milkfat Reduced Fat Milk"],"reduced fat milk":["2% Milkfat Reduced Fat Milk"],"milk":["2% Milkfat Reduced Fat Milk","Vanilla Bean Almond Milk"],"Vanilla Bean Almond Milk":["Vanilla Bean Almond Milk"],"vanilla bean almond milk":["Vanilla Bean Almond Milk"],"vanilla bean milk":["Vanilla Bean Almond Milk"],"vanilla almond milk":["Vanilla Bean Almond Milk"],"bean almond milk":["Vanilla Bean Almond Milk"],"vanilla milk":["Vanilla Bean Almond Milk"],"bean milk":["Vanilla Bean Almond Milk"],"almond milk":["Vanilla Bean Almond Milk"],"Chocolate Sandwich Cookies":["Chocolate Sandwich Cookies"],"chocolate sandwich cookie":["Chocolate Sandwich Cookies"],"chocolate cookie":["Chocolate Sandwich Cookies"],"sandwich cookie":["Chocolate Sandwich Cookies"],"cookie":["Chocolate Sandwich Cookies"]}'
"""
# ENTITY_PRODUCT_NAME_MAP, 
# Key: Entity, Value: List of possible options
{
    "pineapple juice":[  
      "Pineapple Orange Juice"
   ],
   "orange juice":[  
      "Pineapple Orange Juice",
      "Organic Orange Juice Concentrate",
      "Organic Orange Turmeric Juice"
   ],
   "Organic Orange Juice Concentrate":[  
      "Organic Orange Juice Concentrate"
   ],
}
"""


def handle(req):
    """function that search possible options for a synonym entity
    
    Arguments:
        req {str} -- json style request body
    
    Returns:
        str -- json str
    """

    # Config log
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.info("---Enter function: [get-options-list]---")

    # load map, # Key: Entity, Value: List of possible options
    entity_product_name_map = json.loads(ENTITY_PRODUCT_NAME_MAP)

    request_body_dict = json.loads(req)
    
    product_synonym = request_body_dict.get('product_synonym', '')
    product_option_list = entity_product_name_map.get(product_synonym, [])

    function_response_body = {
        'product_option_list': product_option_list,
    }
    
    logging.info("Product_Synonym Entity:{}".format(product_synonym))
    logging.info("Option list length:{}, Option List Content:{}".format(len(product_option_list), product_option_list))
    
    return json.dumps(function_response_body)