import scrapy

class PokedexSpider(scrapy.Spider):
    name = 'pokedex_spider'
    custom_settings = {'DOWNLOAD_DELAY': 0.25}
    start_urls = ['https://www.pokemon.com/us/pokedex/bulbasaur']
    

    def parse(self, response):
    	height, weight = response.css('.pokemon-ability-info.color-bg.color-lightblue.match.active div.column-7 span.attribute-value::text').getall()[:2]
    	height = height.split()
    	height = int(height[0].strip('\'')) * 12 + int(height[1].strip('\"'))

    	category, *abilities = response.css('.pokemon-ability-info.color-bg.color-lightblue.match.active div.column-7.push-7 span.attribute-value::text').getall()
    	abilities_descriptions = response.css('.active div.pokemon-ability-info-detail.match p::text').getall()

    	hp, attack, defense, special_attack, special_defense, speed = [stat.attrib['data-value'] for stat in response.css('.pokemon-stats-info.active li.meter')]

    	yield {
    		'pokemon': response.css('.pokedex-pokemon-pagination-title div::text').get().strip(),
    		'number': int(response.css('.pokedex-pokemon-pagination-title span.pokemon-number::text').get().strip('#')),
    		'image': response.css('.profile-images img.active').attrib['src'],
    		'description': response.css('.version-descriptions.active p.version-y.active::text').get().strip().replace('\n', ' '),
    		'height': height,
    		'weight': float(weight.split()[0]),
    		'category': category,
    		'abilities': dict(zip(abilities, abilities_descriptions)),
    		'type': response.css('.active div.dtm-type a::text').getall(),
    		'weaknesses': list(filter(None, [i.strip() for i in response.css('.active div.dtm-weaknesses span::text').getall()])),
    		'evolutions': list(filter(None, [i.strip() for i in response.css('.column-12.push-1.dog-ear-bl h3.match::text').getall()])),
    		'hp': hp,
    		'attack': attack,
    		'defense': defense,
    		'special_attack': special_attack,
    		'special_defense': special_defense,
    		'speed': speed
    	}

    	next_page = response.css('.pokedex-pokemon-pagination a.next').attrib['href']
    	if next_page != '/us/pokedex/bulbasaur':
    		yield response.follow(next_page, callback=self.parse)

#python -m scrapy runspider pokedex_scraper.py -o pokedex.jl