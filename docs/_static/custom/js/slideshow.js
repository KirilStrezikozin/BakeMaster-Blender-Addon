// slideshow div should have an active content div initialized by default

function slideshow_setSlideByAbsoluteId(slideshowId, contentIndex) {
    let slideshow = document.getElementById(slideshowId);
    // slideshow div should have one content-wrapper div by default
    let content = slideshow.getElementsByClassName("content-wrapper")[0].getElementsByClassName("content");
    // slideshow div should have one footer div by default
    let controls = slideshow.getElementsByClassName("footer")[0].getElementsByClassName("controls")[0].getElementsByClassName("dot");

    // set active content
    for (let i = 0; i < content.length; i++) {
        content[i].className = content[i].className.replace(" active", "");
    }
    content[contentIndex].className += " active";
    // set active control
    for (let i = 0; i < controls.length; i++) {
        controls[i].className = "dot inactive";
    }
    controls[contentIndex].className = "dot active";
}

function slideshow_setSlideByRelativeId(slideshowId, contentRelativeIndex) {
    let slideshow = document.getElementById(slideshowId);
    // slideshow div should have one content-wrapper div by default
    let content = slideshow.getElementsByClassName("content-wrapper")[0].getElementsByClassName("content");

    // find active content
    for (let i = 0; i < content.length; i++) {
        if (content[i].className.endsWith(" active")) {
            let contentIndex = i + contentRelativeIndex;
            if (contentIndex >= content.length) {
                contentIndex = 0;
            }
            else if (contentIndex < 0) {
                contentIndex = content.length - 1;
            }
            slideshow_setSlideByAbsoluteId(slideshowId, contentIndex);
            break;
        }
    }
}