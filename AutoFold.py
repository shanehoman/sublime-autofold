import sublime, sublime_plugin, re

class AutoFoldListener(sublime_plugin.EventListener):
  settings = False
  active = False
  debug = True

  def log(self, str):
    if self.debug:
      print('[AutoFold] '+ str)


  def activate(self, view):
    self.settings = sublime.load_settings('AutoFold.sublime-settings')
    syntax = view.settings().get('syntax').lower()
    extensions = self.settings.get('extensions')
    file_name = view.file_name()

    if not file_name:
      return False

    if not extensions:
      self.log('AutoFold.sublime-settings extensions missing')
      return False

    # run only for selected file extensions
    for ext in extensions:
      if file_name.endswith(ext):
        self.log('Activated for file '+ file_name)
        return True

    return False


  def execute(self, view):
    attrs = self.settings.get('attributes')
    tags = self.settings.get('tags')
    urls = self.settings.get('urls')
    regexps = self.settings.get('regexps')

    if attrs:
      self.fold_attributes(view, attrs)

    if tags:
      self.fold_tags(view, tags)

    if urls:
      self.fold_urls(view, urls)

    if regexps:
      self.fold_regexp(view, regexps)


  def on_activated(self, view):
    if not self.active:
      self.on_load_async(view)


  def on_load_async(self, view):
    self.active = self.activate(view)

    if self.active and self.settings.get('runOnLoad'):
      self.execute(view)


  def on_pre_save_async(self, view):
    if self.active and self.settings.get('runOnSave'):
      self.execute(view)


  def fold_regexp(self, view, regexps):
    for regexp in regexps:
      result = view.find_all(regexp, sublime.IGNORECASE)
      view.fold(result)


  def fold_urls(self, view, params):
    result = view.find_all(params.get('regexp'), sublime.IGNORECASE)
    size = params.get('substr')
    for r in reversed(result):
      if r.size() > size:
        r.b -= size
      else:
        result.remove(r)
    view.fold(result)


  def fold_tags(self, view, tags):
    for tag in tags:
      for m in re.compile(r'(<' + re.escape(tag) + '.*?' + '</' + re.escape(tag) + '>)', re.DOTALL | re.IGNORECASE).\
      finditer(view.substr(sublime.Region(0, view.size()))):
        view.fold(sublime.Region(m.start() + len(tag) + 2, m.end()))


  def fold_attributes(self, view, attrs):
    for attr in attrs:
      result = view.find_all(r'(?<=' + re.escape(attr)
             + '=").*?(?=")', sublime.IGNORECASE)
      view.fold(result)
