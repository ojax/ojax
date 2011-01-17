var activity_template = '{{#items}}\
<div class="activity meta-user-{{username}} meta-type-{{type}} {{#tags}}meta-tag-{{.}} {{/tags}}">\
    <span class="activity-source"><span><img src="/site_media/static/images/icons/{{source}}-24x24.png" alt="">{{#capitalise}}{{type}}{{/capitalise}}</span></span>\
    <a href="#" class="activity-title">{{title}}</a>\
    <span class="activity-meta">— {{#capitalise}}{{type}} {{/capitalise}}  by {{username}}, {{dt}}.</span>\
    \
    <a href="#" class="yum-button comment"><span>0 Comments</span></a>\
    <a href="#" class="actions"></a>\
</div>{{/items}}'

// var comment_template = <li class="comment-body">
//     <div class="comment-meta">
//         <div class="comment-time">{{ comment.created|timesince }}</div>
//         <div class="comment-author"><em>{{ comment.author }}</em> said:</div>
//     </div>
//     
//     <p>{{comment.comment}}</p>
// </li>


$(document).ready(function(){
    $("#filter-bar").click(function(){
        $("#filter-container").slideToggle();
        return false;
    });
    
    $(".comment").click(function(){
        // $(this).parent().toggleClass("expanded");
        // $(this).removeClass("updated");
        $(this).parent().children(".comments-container").toggle()
        return false;
    });
    
    $(".edit-project").click(function(){
        return false;
    });
    
    
    $("#filter-sort-control .filter-button").click(function(){
        $(this).siblings().removeClass("selected");
        $(this).addClass("selected");
        return false;
    });
    
    $(".filter-options-container .filter-button:not(.all)").click(function(){
        $(this).toggleClass("selected");
        $(this).siblings(".all").removeClass("selected");

        if( $(this).parent().has(".selected").length == 0 ) {
            $(this).parent().children(".all").addClass("selected");
        }
        
        populate_stream();
        
        return false;
    });
    
    $(".filter-options-container .filter-button.all ").click(function(){
        $(this).siblings().removeClass("selected");
        $(this).addClass("selected");
        
        populate_stream();
        
        return false;
    });
    
//    $("#filter-users-control .filter-button:not(.all)").click(function(){
//        
//        var make_visible = "";
//        var make_hidden = ".activity:not(";
//    
//        $(this).parent().children(".selected").each(function(i){
//        
//            make_visible += ".activity.meta"+$(this).attr("id").substring(6)+", ";
//            make_hidden += ".meta"+$(this).attr("id").substring(6)+", ";
//        
//        });
//        make_hidden += ")";
//        
//        if (make_visible == "") {
//            $(".activity").slideUp();
//            return false;
//        }
//        
//        $(make_visible).slideDown();        
//        $(make_hidden).slideUp();
//        
//        return false;
//    });
    
    function populate_stream() {
        var visible_tags = visible_users = visible_type = hidden_tags = hidden_users = hidden_type = "";
    
        $("#filter-tags-control .selected:not(.all)").each(function(i){
            visible_tags += ".activity:not(.meta"+$(this).attr("id").substring(6)+")";    
//            hidden_tags += ".activity.meta"+$(this).attr("id").substring(6)+","; 
        });
        
        $("#filter-users-control .selected:not(.all)").each(function(i){
            visible_users += ".activity:not(.meta"+$(this).attr("id").substring(6)+")";
//            hidden_users += ".activity.meta"+$(this).attr("id").substring(6)+",";  
        });
        
        $("#filter-type-control .selected:not(.all)").each(function(i){
            visible_type += ".activity:not(.meta"+$(this).attr("id").substring(6)+")";
//            hidden_type += ".activity.meta"+$(this).attr("id").substring(6)+",";   
        });
        

        $(".activity").removeClass("hide-this");
        
        
        if( $("#filter-tags-control").has(".selected.all").length == 0) {
            $(visible_tags).addClass("hide-this");
        }
        if( $("#filter-users-control").has(".selected.all").length == 0) {
            $(visible_users).addClass("hide-this");
        }
        if( $("#filter-type-control").has(".selected.all").length == 0) {
            $(visible_type).addClass("hide-this");
        }
        
        $(".activity:not(.hide-this)").slideDown()
        $(".activity.hide-this").slideUp()
        
        // count visible
        // Select bla bla > count limit x
        
        //$(".activity:visible:gt(4)").hide();
    }
    
//    $("#filter-tags-control .filter-button:not(.all), #filter-users-control .filter-button:not(.all), #filter-type-control .filter-button:not(.all)").click(function(){
//        var visible_tags = "";
//        var visible_users = "";
//        var visible_type = "";
//        var hidden_tags = "";
//        var hidden_users = "";
//        var hidden_type = "";
//    
//        $("#filter-tags-control .selected:not(.all)").each(function(i){
//            visible_tags += ".activity:not(.meta"+$(this).attr("id").substring(6)+")";    
//            hidden_tags += ".activity.meta"+$(this).attr("id").substring(6)+","; 
//        });
//        
//        $("#filter-users-control .selected:not(.all)").each(function(i){
//            visible_users += ".activity:not(.meta"+$(this).attr("id").substring(6)+")";
//            hidden_users += ".activity.meta"+$(this).attr("id").substring(6)+",";  
//        });
//        
//        $("#filter-type-control .selected:not(.all)").each(function(i){
//            visible_type += ".activity:not(.meta"+$(this).attr("id").substring(6)+")";
//            hidden_type += ".activity.meta"+$(this).attr("id").substring(6)+",";   
//        });
//        
        //alert(visible_tags + visible_users + visible_type);
//        
//        $(".activity").show();
//        $(visible_tags).slideUp();
//        $(visible_users).slideUp();
//        $(visible_type).slideUp();
        //$(hidden_tags + hidden_users + hidden_type).slideDown();
//        
//        
//    });

updatesToJSONFeed = function(initialJSON, newJSON){
	
	var logIt = function(msg) {
      try {
        console.log(msg);
      } catch(err) {}
    }

    var comparison = false;
    var objects_changed = 0;
    var offset = 0;

    function findNumberOfNewObjects(oldFeed, newFeed) {
        if (typeof newFeed == 'object' && typeof oldFeed == 'object') {
            var property = propertyOffset = 0;

            try {
                comparison = compare(oldFeed[property], newFeed[propertyOffset]);
            }
            catch(e) {
				logIt('Failed on first object')
			}
			
            while (!comparison && propertyOffset < oldFeed.length) {
                objects_changed++;
                propertyOffset++;
                try {
                    comparison = compare(oldFeed[property], newFeed[propertyOffset]);
                }
                catch(e) {
					logIt('Failed on object '+propertyOffset)
				}
            }
            // Return the number of new items or else return false
            return objects_changed || false;
        }
        // If we're dealing with anything other than objects then return false
        return false;
    }

    function compare(a, b) {
        if (typeof a == 'object') {
            for (var property in a) {
                comparison = compare(a[property], b[property]);
                if (!comparison) return false;
            }
            return comparison;
        }
        return (a == b);
    }

    return findNumberOfNewObjects(initialJSON, newJSON);
}


});