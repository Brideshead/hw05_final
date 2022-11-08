from django import forms

from posts.models import Comment, Post


class PostForm(forms.ModelForm):
    """
    Создание объекта, который передается в качестве
    переменной form в контекст шаблона templates/create_post.html
    """

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_text = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Картинка поста',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_text = {
            'text': 'Текст комментария',
        }
