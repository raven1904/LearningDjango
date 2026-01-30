from django.shortcuts import render
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import Note
from django.urls import reverse_lazy

class NoteListView(ListView):
    model = Note
    template_name = 'core/note_list.html'
    context_object_name = 'notes'

class NoteDetailView(DetailView):
    model = Note
    template_name = 'core/note_detail.html'

class NoteCreateView(CreateView):
    model = Note
    fields = ['title', 'content']
    template_name = 'core/note_form.html'
    success_url = reverse_lazy('note-list')

class NoteUpdateView(UpdateView):
    model = Note
    fields = ['title', 'content']
    template_name = 'core/note_form.html'
    success_url = reverse_lazy('note-list')

class NoteDeleteView(DeleteView):
    model = Note
    template_name = 'core/note_confirm_delete.html'
    success_url = reverse_lazy('note-list')
