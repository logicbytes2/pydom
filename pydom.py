"""
pydom.py

A fully JavaScript-like DOM wrapper in Python using BeautifulSoup.
Supports:
- Selection: getElementById, getElementsByClassName, getElementsByTagName, querySelector(All)
- Creation: createElement
- Traversal: parentElement, children, closest, matches, contains
- Manipulation: appendChild, prepend, insertBefore, replaceChild, remove, cloneNode
- Insertion: append, prependText, insertAdjacentHTML, insertAdjacentElement
- Content: innerHTML, textContent
- Classes: classList (addClass, removeClass)
- Styling: style property
- Events: addEventListener, removeEventListener, triggerEvent
- Shortcuts: document.body, document.head
"""

from bs4 import BeautifulSoup

# -----------------------------
# Element class
# -----------------------------
class Element:
    def __init__(self, tag):
        self.tag = tag
        self._events = {}

        # Initialize style dictionary
        self._style = {}
        if tag.has_attr("style"):
            for s in tag["style"].split(";"):
                if s.strip():
                    key, value = s.split(":")
                    self._style[key.strip()] = value.strip()

    # ----------------- innerHTML / textContent -----------------
    @property
    def innerHTML(self):
        return "".join(str(child) for child in self.tag.contents)

    @innerHTML.setter
    def innerHTML(self, html_str):
        self.tag.clear()
        new_content = BeautifulSoup(html_str, "html.parser")
        for child in new_content.contents:
            self.tag.append(child)

    @property
    def textContent(self):
        return self.tag.get_text()

    @textContent.setter
    def textContent(self, text_str):
        self.tag.clear()
        self.tag.append(text_str)

    # ----------------- classList -----------------
    @property
    def classList(self):
        return self.tag.get("class", [])

    def addClass(self, cls):
        classes = self.tag.get("class", [])
        if cls not in classes:
            classes.append(cls)
            self.tag['class'] = classes

    def removeClass(self, cls):
        classes = self.tag.get("class", [])
        if cls in classes:
            classes.remove(cls)
            if classes:
                self.tag['class'] = classes
            else:
                del self.tag['class']

    # ----------------- parent / children -----------------
    @property
    def parentElement(self):
        parent = self.tag.parent
        return Element(parent) if parent else None

    @property
    def children(self):
        return [Element(child) for child in self.tag.find_all(recursive=False)]

    # ----------------- remove -----------------
    def remove(self):
        self.tag.decompose()

    # ----------------- get/set attribute -----------------
    def getAttribute(self, attr):
        return self.tag.get(attr)

    def setAttribute(self, attr, value):
        self.tag[attr] = value

    # ----------------- querySelector / querySelectorAll -----------------
    def querySelector(self, selector):
        el = self.tag.select_one(selector)
        return Element(el) if el else None

    def querySelectorAll(self, selector):
        return [Element(el) for el in self.tag.select(selector)]

    # ----------------- style -----------------
    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, style_dict):
        self._style.update(style_dict)
        self.tag["style"] = "; ".join(f"{k}: {v}" for k, v in self._style.items())

    # ----------------- event listeners -----------------
    def addEventListener(self, event, callback):
        if event not in self._events:
            self._events[event] = []
        self._events[event].append(callback)

    def removeEventListener(self, event, callback):
        if event in self._events:
            self._events[event] = [cb for cb in self._events[event] if cb != callback]

    def triggerEvent(self, event, *args, **kwargs):
        if event in self._events:
            for callback in self._events[event]:
                callback(*args, **kwargs)

    # ----------------- matches / closest / contains -----------------
    def matches(self, selector):
        return bool(self.tag.select_one(f":scope{selector}"))

    def closest(self, selector):
        el = self
        while el is not None:
            if el.matches(selector):
                return el
            el = el.parentElement
        return None

    def contains(self, other_element):
        if not isinstance(other_element, Element):
            raise TypeError("contains expects an Element instance")
        return other_element.tag in self.tag.descendants

    # ----------------- appendChild / prepend / insertBefore / replaceChild -----------------
    def appendChild(self, child):
        if isinstance(child, Element):
            self.tag.append(child.tag)
        else:
            raise TypeError("appendChild expects an Element instance")

    def prepend(self, child):
        if isinstance(child, Element):
            if self.tag.contents:
                self.tag.insert(0, child.tag)
            else:
                self.tag.append(child.tag)
        else:
            raise TypeError("prepend expects an Element instance")

    def insertBefore(self, new_child, reference_child):
        if not isinstance(new_child, Element) or not isinstance(reference_child, Element):
            raise TypeError("insertBefore expects Element instances")
        index = self.tag.contents.index(reference_child.tag)
        self.tag.insert(index, new_child.tag)

    def replaceChild(self, new_child, old_child):
        if not isinstance(new_child, Element) or not isinstance(old_child, Element):
            raise TypeError("replaceChild expects Element instances")
        index = self.tag.contents.index(old_child.tag)
        self.tag.contents[index] = new_child.tag

    # ----------------- cloneNode -----------------
    def cloneNode(self, deep=True):
        html_str = str(self.tag)
        if not deep:
            temp_soup = BeautifulSoup(html_str, "html.parser")
            temp_tag = temp_soup.find(self.tag.name)
            temp_tag.clear()
        else:
            temp_tag = BeautifulSoup(html_str, "html.parser").find(self.tag.name)
        return Element(temp_tag)

    # ----------------- append / prependText convenience -----------------
    def append(self, content):
        if isinstance(content, Element):
            self.tag.append(content.tag)
        elif isinstance(content, str):
            new_content = BeautifulSoup(content, "html.parser")
            for child in new_content.contents:
                self.tag.append(child)
        else:
            raise TypeError("append expects Element or HTML string")

    def prependText(self, content):
        if isinstance(content, Element):
            if self.tag.contents:
                self.tag.insert(0, content.tag)
            else:
                self.tag.append(content.tag)
        elif isinstance(content, str):
            new_content = BeautifulSoup(content, "html.parser")
            for child in reversed(new_content.contents):
                self.tag.insert(0, child)
        else:
            raise TypeError("prepend expects Element or HTML string")

    # ----------------- insertAdjacentHTML / insertAdjacentElement -----------------
    def insertAdjacentHTML(self, position, html_str):
        new_content = BeautifulSoup(html_str, "html.parser")
        if position == "beforebegin":
            for child in reversed(new_content.contents):
                self.tag.insert_before(child)
        elif position == "afterbegin":
            for child in reversed(new_content.contents):
                self.tag.insert(0, child)
        elif position == "beforeend":
            for child in new_content.contents:
                self.tag.append(child)
        elif position == "afterend":
            for child in new_content.contents:
                self.tag.insert_after(child)
        else:
            raise ValueError("Invalid position for insertAdjacentHTML")

    def insertAdjacentElement(self, position, element):
        if not isinstance(element, Element):
            raise TypeError("insertAdjacentElement expects an Element instance")
        if position == "beforebegin":
            self.tag.insert_before(element.tag)
        elif position == "afterbegin":
            self.tag.insert(0, element.tag)
        elif position == "beforeend":
            self.tag.append(element.tag)
        elif position == "afterend":
            self.tag.insert_after(element.tag)
        else:
            raise ValueError("Invalid position for insertAdjacentElement")


# -----------------------------
# Document class
# -----------------------------
class Document:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, "html.parser")

    # DOM selection
    def getElementById(self, element_id):
        tag = self.soup.find(id=element_id)
        return Element(tag) if tag else None

    def getElementsByClassName(self, class_name):
        return [Element(tag) for tag in self.soup.find_all(class_=class_name)]

    def getElementsByTagName(self, tag_name):
        return [Element(tag) for tag in self.soup.find_all(tag_name)]

    def querySelector(self, selector):
        tag = self.soup.select_one(selector)
        return Element(tag) if tag else None

    def querySelectorAll(self, selector):
        return [Element(tag) for tag in self.soup.select(selector)]

    # Create new element
    def createElement(self, tag_name):
        tag = self.soup.new_tag(tag_name)
        return Element(tag)

    # JS-like shortcuts
    @property
    def body(self):
        tag = self.soup.body
        return Element(tag) if tag else None

    @property
    def head(self):
        tag = self.soup.head
        return Element(tag) if tag else None

        # ----------------- document.title -----------------
    @property
    def title(self):
        title_tag = self.soup.title
        return title_tag.get_text() if title_tag else ""

    @title.setter
    def title(self, value):
        if self.soup.title:
            self.soup.title.string = value
        else:
            new_title = self.soup.new_tag("title")
            new_title.string = value
            if self.soup.head:
                self.soup.head.append(new_title)
            else:
                head_tag = self.soup.new_tag("head")
                head_tag.append(new_title)
                if self.soup.html:
                    self.soup.html.insert(0, head_tag)
                else:
                    self.soup.insert(0, head_tag)

    # ----------------- getElementsByName -----------------
    def getElementsByName(self, name):
        return [Element(tag) for tag in self.soup.find_all(attrs={"name": name})]
    
    # ----------------- document.write -----------------
    def write(self, html_str):
        """Writes HTML into the document body, replacing existing content."""
        
        # Ensure <body> exists
        if not self.soup.body:
            body_tag = self.soup.new_tag("body")
            if self.soup.html:
                self.soup.html.append(body_tag)
            else:
                html_tag = self.soup.new_tag("html")
                html_tag.append(body_tag)
                self.soup.append(html_tag)

        # Clear existing body content
        self.soup.body.clear()

        # Parse new HTML and insert
        new_content = BeautifulSoup(html_str, "html.parser")
        for child in new_content.contents:
            self.soup.body.append(child)

