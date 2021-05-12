var timer = null;
var pad_num = number => number <= 9 ? `0${number}`.slice(-2) : number;

async function load_data(file) {
	const data = await d3.csv(file);
	return data;
}

function preload_img(array) {
	var list = [];

	for (var i = 0; i < array.length; i++) {
		var img = new Image();
		list.push(img);
		img.src = array[i];
	}
}

function rotate_img(sneaker) {
	var i = 1;

	timer = setInterval(function() {
		i += 1;

		if (i == 37) {
			i = 1;
		}

		d3.select('img')
			.attr('src', 'images/' + sneaker + '_' + pad_num(i) + '.jpg');
	}, 165);
}

async function draw_chart(file) {
	const data = await load_data(file);
	
	//cache images
	img = [];
	for (var i = 0; i < data.length; i++) {
		for (var j = 1; j < 37; j++) {
			img.push('images/' + data[i]['Sneaker Name'] + '_' + pad_num(j) + '.jpg');
		}
	}
	preload_img(img);

	var margin = {top: 75, right: 150, bottom: 50, left: 60};
	var width = 750 - margin.left - margin.right;
	var height = 800 - margin.top - margin.bottom;

	var svg = d3.select('div')
		.append('svg')
			.attr('width', width + margin.left + margin.right)
			.attr('height', height + margin.top + margin.bottom);

	// title
	svg.append('text')
		.attr('id', 'title')
		.attr('text-anchor', 'left')
		.attr('x', 10)
		.attr('y', 40)
		.text('Sneaker Resale Market')
		.style('font-family', 'Monaco, monospace')
		.style('fill', 'white')
		.style('font-size', '2em');

	// x-axis label
	svg.append('text')
		.attr('class', 'axisLabel')
		.attr('text-anchor', 'middle')
		.attr('x', height / 2)
		.attr('y', height + margin.top + 40)
		.text('retail price ($)');

	// y-axis label
	svg.append('text')
		.attr('class', 'axisLabel')
		.attr('text-anchor', 'middle')
		.attr('x', -height / 2 - margin.bottom)
		.attr('y', 15)
		.attr('transform', 'rotate(-90)')
		.text('price premium (%)');

	svg = svg.append('g')
			.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

	// x axis
	var x = d3.scaleLinear()
		.domain([120, 230])
		.range([0, width]);
	svg.append('g')
		.attr('class', 'axis')
		.attr('transform', 'translate(0,' + height + ')')
		.call(d3.axisBottom(x));
	
	// y axis
	var y = d3.scaleLinear()
		.domain([200, 900])
		.range([height, 0]);
	svg.append('g')
		.attr('class', 'axis')
		.call(d3.axisLeft(y));

	// bubble size
	var z = d3.scaleSqrt()
		.domain([0, 5000])
		.range([0, 25]);

	// bubble color
	var color = d3.scaleOrdinal()
		.domain(['Off-White', 'Yeezy']).
		range(['#05ebfc', '#fc05e7']);

	var tooltip;

	// tooltip functions
	var show_tooltip = function(event, d) {
		console.log('show');
		tooltip = d3.select('div')
			.append('div')
			.style('opacity', 1)
			.attr('class', 'tooltip')
			.style('background-color', 'white')
			.style('border-radius', '4px')
			.style('color', 'black')
			.style('width', '420px')
			.style('left', ((d3.pointer(event)[0] - 25) + 'px'))
			.style('top', ((d3.pointer(event)[1] + 100) + 'px'));
		var tooltip_title = tooltip.append('div')
			.attr('class', 'tooltip_title')
			.html(d['Sneaker']);
		var tooltip_info = tooltip.append('div')
			.attr('class', 'tooltip_info');
		tooltip_image = tooltip_info.append('img')
			.attr('class', 'tooltip_image')
			.attr('type', 'image/jpeg')
			.attr('src', 'images/' + d['Sneaker Name'] + '_01.jpg');
		var tooltip_details = tooltip_info.append('div')
			.attr('class', 'tooltip_details')
			.html('<text> retail price: $' + d['Retail Price'] + '</text><br>'
				+ '<text> avg sale price: $' + d['Avg Sale Price'] + '</text><br>'
				+ '<text> avg price premium: ' + d['Avg Price Premium'] + '%</text><br>'
				+ '<text> sales: ' + d['Sales'] + '</text>');
		tooltip.transition()
			.duration(1000);

		rotate_img(d['Sneaker Name']);
	}

	var move_tooltip = function(event, d) {
		tooltip
			.style('left', ((d3.pointer(event)[0] - 25) + 'px'))
			.style('top', ((d3.pointer(event)[1] + 100) + 'px'));
		console.log('move');
	}

	var hide_tooltip = function(event, d) {
		tooltip
			.transition()
			.duration(1000)
			.style('opacity', 0);

		clearInterval(timer);
		tooltip.remove();
		console.log('hide');
	}

	// dots
	svg.append('g')
		.selectAll('dot')
		.data(data)
		.enter()
		.append('circle')
			.attr('class', function(d) { return 'bubbles ' + d['Brand']; })
			.attr('cx', function(d) { return x(d['Retail Price']); })
			.attr('cy', function(d) { return y(d['Avg Price Premium']); })
			.attr('r', function(d) { return z(d['Sales']); })
			.style('fill', function(d) { return color(d['Brand']); })
		.on('mouseover', show_tooltip)
		.on('mousemove', move_tooltip)
		.on('mouseleave', hide_tooltip);

	// color legend
	svg.append('text')
		.attr('text-anchor', 'left')
		.attr('x', 562)
		.attr('y', width / 2 - 20)
		.text('Brand')
		.style('fill', 'white')
		.style('font-family', 'Monaco, monospace')
		.style('font-size', '1em');
	svg.selectAll('color_legend')
		.data(['Off-White', 'Yeezy'])
		.enter()
		.append('circle')
			.attr('cx', 565)
			.attr('cy', function(d, i) { return i * 20 + (width / 2); })
			.attr('r', 3)
			.style('fill', function(d) { return color(d); });
	svg.selectAll('color_label')
		.data(['Off-White', 'Yeezy'])
		.enter()
		.append('text')
			.attr('text-anchor', 'left')
			.attr('x', 575)
			.attr('y', function(d, i) { return i * 20 + (width / 2) + 5; })
			.text(function(d) { return d; })
			.style('fill', function(d) { return color(d); })
			.style('font-family', 'Monaco, monospace')
			.style('font-size', '.85em');

	// size legend
	const size_legend = ['100', '2000', '5000'];
	svg.append('text')
		.attr('text-anchor', 'left')
		.attr('x', 562)
		.attr('y', width / 2 + 75)
		.text('Sales')
		.style('fill', 'white')
		.style('font-family', 'Monaco, monospace')
		.style('font-size', '1em');
	svg.selectAll('size_legend')
		.data(size_legend)
		.enter()
		.append('circle')
			.attr('cx', 590)
			.attr('cy', function(d) { return height - 267 - z(d); })
			.attr('r', function(d) { return z(d); })
			.style('fill', 'none')
			.attr('stroke', 'white');
	svg.selectAll('size_label')
		.data(size_legend)
		.enter()
		.append('text')
			.attr('x', 620)
			.attr('y', function(d, i) { return height - 270 - (15 * i); })
			.text(function(d) { return d; })
			.style('font-family', 'Monaco, monospace')
			.style('font-size', '.85em')
			.style('fill', 'white');
}

draw_chart('price_premium.csv');