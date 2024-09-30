### [{{project.name}}]({{project.web_url}})
> {{handle_option}} {{handle_branch}}{% for commit in commits %}
> {{ commit.author.name }}： [{{ commit.title }}]({{ commit.url }}){% endfor %}