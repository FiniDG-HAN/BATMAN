var ctx = document.getElementById('chart').getContext('2d');

Chart.defaults.global.defaultFontColor = '#FFF';

var chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['1971-1975',
             '1976-1980',
             '1981-1985',
             '1986-1990',
             '1991-1995',
             '1996-2000',
             '2001-2005',
             '2006-2010',
             '2011-2015',
             '2016-2018'],
    datasets: [{
      label: 'Momordica charantia (bitter gourd)',
      data: [2, 14, 34, 32, 44, 64, 115, 191, 273, 130],
      borderColor: 'rgba(107,186,30,0.9)',
      backgroundColor: 'rgba(112,163,70,0.5)'
    },
    {
      label: 'Dioscorea (yam)',
      data: [15, 10, 29, 20, 26, 41, 143, 246, 423, 216],
      borderColor: 'rgba(212,137,72,0.9)',
      backgroundColor: 'rgba(191,151,117,0.5)'
    }]
  },
  options: {
    title: {
      display: true,
      text: 'PubMed article count per 5 years',
      fontSize: 16
    },
    scales: {
      xAxes: [{
        gridLines: {
          color: '#777'
        }
      }],
      yAxes: [{
        gridLines: {
          color: '#999'
        }
      }]
    }
  }
});
