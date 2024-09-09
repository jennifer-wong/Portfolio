var timer = null;
var pad_num = number => number <= 9 ? `0${number}`.slice(-2) : number;


/**
 * Load data from a file
 * @param {string} file - file name of data
 * @return {Array} data - array of objects
 */
async function load_data(file) {
	const data = await d3.csv(file);
	return data;
}


/**
 * Constructs array of HTMLImageElement instances
 * @param {array} array - array of image file names
 * @return {void} Nothing
 */
function preload_img(array) {
	var list = [];

	for (var i = 0; i < array.length; i++) {
		var img = new Image();
		list.push(img);
		img.src = array[i];
	}
}


/**
 * Loops through images
 * @param {string} sneaker - name of sneaker
 * @return {void} Nothing
 */
function rotate_img(sneaker) {
	var i = 1;

	timer = setInterval(
		function() {
			i += 1;

			if (i == 37) {
				i = 1;
			}

			d3.select('img')
				.attr('src', 'images/' + sneaker + '_' + pad_num(i) + '.jpg');
		},
		165
	);
}


/**
 * Creates chart
 * @param {string} file - file name of data
 * @return {void} Nothing
 */
async function create_chart(file) {
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
	var width = 900 - margin.left - margin.right;
	var height = 550 - margin.top - margin.bottom;

	var svg = d3.select('div')
		.append('svg')
		.attr('width', width + margin.left + margin.right)
		.attr('height', height + margin.top + margin.bottom);

	// title
	svg.append('text')
		.attr('id', 'title')
		.attr('text-anchor', 'left')
		.attr('x', 0)
		.attr('y', 40)
		.text('Nike x Off-White Sneaker Resale')
		.style('font-family', 'Monaco, monospace')
		.style('fill', 'white')
		.style('font-size', '2em');

	// x-axis label
	svg.append('text')
		.attr('class', 'axisLabel')
		.attr('text-anchor', 'middle')
		.attr('x', height / 2 + 200)
		.attr('y', height + margin.top + 40)
		.text('Retail Price ($)');

	// y-axis label
	svg.append('text')
		.attr('class', 'axisLabel')
		.attr('text-anchor', 'middle')
		.attr('x', -height / 2 - 75)
		.attr('y', 15)
		.attr('transform', 'rotate(-90)')
		.text('Price Premium (%)');

	svg = svg.append('g')
		.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

	// x axis
	var x = d3.scaleLinear()
		.domain([120, 260])
		.range([0, width]);
	svg.append('g')
		.attr('class', 'axis')
		.attr('transform', 'translate(0,' + height + ')')
		.call(d3.axisBottom(x));
	
	// y axis
	var y = d3.scaleLinear()
		.domain([0, 1000])
		.range([height, 0]);
	svg.append('g')
		.attr('class', 'axis')
		.call(d3.axisLeft(y));

	// bubble size
	var z = d3.scaleSqrt()
		.domain([0, 1000])
		.range([0, 25]);

	// bubble color
	var color = d3.scaleOrdinal()
		.domain(['Off-White'])
		.range(['#FAF9F6']);

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
			.html(d['Display Sneaker Name']);
		var tooltip_info = tooltip.append('div')
			.attr('class', 'tooltip_info');
		tooltip_image = tooltip_info.append('img')
			.attr('class', 'tooltip_image')
			.attr('type', 'image/jpeg')
			.attr('src', 'images/' + d['Sneaker Name'] + '_01.jpg');
		var tooltip_details = tooltip_info.append('div')
			.attr('class', 'tooltip_details')
			.html(
				'<text> retail price: $' + d['Retail Price'] + '</text><br>'
				+ '<text> avg sale price: $' + d['Avg Sale Price'] + '</text><br>'
				+ '<text> price premium: ' + d['Avg Price Premium'] + '%</text><br>'
				+ '<text> sales: ' + d['# of Sales'] + '</text>'
			);
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
			.attr('r', function(d) { return z(d['# of Sales']); })
			.style('fill', function(d) { return color(d['Brand']); })
		.on('mouseover', show_tooltip)
		.on('mousemove', move_tooltip)
		.on('mouseleave', hide_tooltip);

	// size legend
	const size_legend = ['100', '500', '1000'];
	svg.append('text')
		.attr('text-anchor', 'left')
		.attr('x', 730)
		.attr('y', width / 3)
		.text('Sales')
		.style('fill', 'white')
		.style('font-family', 'Monaco, monospace')
		.style('font-size', '1em');
	svg.selectAll('size_legend')
		.data(size_legend)
		.enter()
		.append('circle')
			.attr('cx', 753)
			.attr('cy', function(d) { return height - 215 - z(d); })
			.attr('r', function(d) { return z(d); })
			.style('fill', 'none')
			.attr('stroke', 'white');
	svg.selectAll('size_label')
		.data(size_legend)
		.enter()
		.append('text')
			.attr('x', 785)
			.attr('y', function(d, i) { return height - 220 - (15 * i); })
			.text(function(d) { return d; })
			.style('font-family', 'Monaco, monospace')
			.style('font-size', '.85em')
			.style('fill', 'white');
}


create_chart('off-white resale data.csv');