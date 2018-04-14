function obosCharts(domid,title,dataUrl) {
    $.ajax({url:dataUrl,dataType:"json",type:"get",success:function(data){
        Highcharts.stockChart(domid, {
        title: {
            text: title
        },
        rangeSelector: {
            buttons: [{
               type: 'hour',
               count: 1,
                text: '1h'
            }, {
                type: 'day',
                count: 1,
                text: '1D'
            }, {
                type: 'all',
                count: 1,
                text: 'All'
            }],
            selected: 1,
            inputEnabled: false
        },
        series: [{
            name: title,
            type: 'candlestick',
            data: data,
            tooltip: {
                valueDecimals: 2
            }
        }]
        });
    }});
}


//$(document).ready(function(){
////    $.ajax({
////        type:'GET',
////        url:'{%url "market"%}',
////        dataType:'json',
////        success:function(data){
////            console.log(data);
////            obosCharts('obos-chart','000300.SH',{{obos_data}});
////        }
////    })
//    obosCharts('obos-chart',obos_select,'{{obos_data}}');
//    $('.obos-choose').click(function(){
//        obos_select = event.target.id;
//        $.ajax({
//            type:'POST',
//            url:'{%url "market"%}',
//            data:JSON.stringify({
//                'obos_select':obos_select,
////                'csrfmiddlewaretoken': '{{ csrf_token }}',
//            }),
//            dataType: "json",
//            contentType: "application/json",
//            success: function(e){
//                console.log(e);
//            },
//        });
//        obosCharts('obos-chart',obos_select,'{{obos_data}}');
//    });
//});

//$(document).ready(function() {
//    $('#volatility-table').dataTable({
//        "dom": 'tip'
//    });
//    $('#turnover-table').dataTable({
//        "dom": 'tip'
//    });
//} );