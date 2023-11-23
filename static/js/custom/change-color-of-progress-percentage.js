$(function() {
    var score = parseInt($('.score-number').text().trim().slice(-3, -1));
    var color = 'darkgray';
    if (!isNaN(score)) {
        if (score >= 35) {
            color = 'firebrick';
        }
        if (score >= 65) {
            color = 'khaki';
        }
        if (score >= 80) {
            color = 'mediumseagreen';
        }
        $('.score-number').css('color', color);
    }
    else {
        $('.score-number').css('color', '#747474');
    }
});
