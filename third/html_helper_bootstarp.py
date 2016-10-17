#!/usr/bin/env python
#coding:utf8

#from django.utils.safestring import mark_safe

class PageInfo(object):
    def __init__(self,current,totalItem,peritems=5):
        self.__current = current
        self.__totalItem = totalItem
        self.__peritems = peritems

    @property
    def From(self):
        return (self.__current-1) * self.__peritems

    @property
    def To(self):
        return self.__current * self.__peritems

    @property
    def TotalPage(self): #总页数
        result = divmod(self.__totalItem,self.__peritems)
    
        if result[1] ==0:
            return result[0]
        else:
            return result[0]+1

def Custompager(baseurl,currentPage,totalpage):
    '''
    baseurl:基础页
    currentPage:当前页
    totalpage:总页数
    #总页数<11
    #0 -- totalpage
    #总页数>11
    #当前页大于5 currentPage-5 -- currentPage+5
    #currentPage+5是否超过总页数,超过总页数，end就是总页数
    #当前页小于5 0 -- 10

    '''

    perPage = 10

    begin = 0
    end = 0
  
    begin_two = 0
    end_two = 0
    

    if isinstance(currentPage,int):
        if totalpage <= 10:
            begin = 0
            end = totalpage
        else:
            if currentPage > 5:
                begin = currentPage - 6
                end = currentPage + 4
                if end > totalpage:
                    end = totalpage
            else:
                begin = 0
                end = 10
    
    
        if currentPage > 10:
            begin_two = 9
        if currentPage < totalpage - 10:
            end_two = 9
    
        pager_list = []
    
    
        cs='''
            <nav>
              <ul class="pagination">
    
            '''
    
        pager_list.append(cs)
    
    
    
        if currentPage <= 1:
            first =  "<li  class='disabled'><a>首页</a></li>"
        else:
            first = "<li><a class='act_post' href='%s?page_id=%s'>首页</a></li>"%(baseurl,1)
        pager_list.append(first)
    
    
    
    
        if currentPage <= 1:
            prev = "<li  class='disabled'><a   aria-label='Previous'><span aria-hidden='true'>上一页</span></a></li>"
        else:
            prev = "<li><a class='act_post' href='%s?page_id=%s' aria-label='Previous'><span aria-hidden='true'>上一页</span></a></li>"%(baseurl,currentPage-1)
        pager_list.append(prev)
    
    
        if begin_two:
            prev_two = "<li><a class='act_post' href='%s?page_id=%s'>...</a></li>"%(baseurl,currentPage-begin_two)
            pager_list.append(prev_two)
    
    
        temp = ''
        for i in range(begin+1,end+1):
            if i == currentPage:
                temp = "<li class='disabled'><a   class='list-group-item active'>%d</a></li>"%(i)
            else:
                temp = "<li><a class='act_post' href='%s?page_id=%s'>%d</a></li>"%(baseurl,i,i)
            pager_list.append(temp)
    
    
        if end_two:
            
            next_two = "<li><a class='act_post' href='%s?page_id=%s'>...</a></li>"%(baseurl,currentPage + end_two)
            pager_list.append(next_two)
    
    
        if currentPage >= totalpage:
            next = "<li class='disabled'><a   aria-label='Next'><span aria-hidden='true'>下一页</span></a></li>"
        else:
            next = "<li><a class='act_post' href='%s?page_id=%s'aria-label='Next'><span aria-hidden='true'>下一页</span></a></li>"%(baseurl,currentPage + 1)
        pager_list.append(next)
    
    
    
        if currentPage >= totalpage:
            last = "<li class='disabled'><a  >末页</a></li>"
        else:
            last = "<li><a class='act_post'  href='%s?page_id=%s'>末页</a></li>"%(baseurl,totalpage)
    
        pager_list.append(last)
    
    
        cs='''
    
              </ul>
            </nav>
    
        '''
    
        pager_list.append(cs)    
        
        
    else:    

        page = currentPage.split('&')[0].split('=')[1]
        
        page = int(page)
    
        url = '&'.join(currentPage.split('&')[1:])
        
        if totalpage <= 10:
            begin = 0
            end = totalpage
        else:
            if page > 5:
                begin = page - 6
                end = page + 4
                if end > totalpage:
                    end = totalpage
            else:
                begin = 0
                end = 10
    
    
        if page > 10:
            begin_two = 9
        if page < totalpage - 10:
            end_two = 9
    
        pager_list = []
    
    
        cs='''
        	<nav>
    		  <ul class="pagination">
    
            '''
    
        pager_list.append(cs)
    
    
    
        if page <= 1:
            first =  "<li class='disabled'><a  >首页</a></li>"
        else:
            first = "<li><a class='act_post' href='%s?page_id=%s'>首页</a></li>"%(baseurl,str(1)+"&"+url)
        pager_list.append(first)
    
    
    
    
        if page <= 1:
            prev = "<li  class='disabled'><a   aria-label='Previous'><span aria-hidden='true'>上一页</span></a></li>"
        else:
            prev = "<li><a class='act_post' href='%s?page_id=%s' aria-label='Previous'><span aria-hidden='true'>上一页</span></a></li>"%(baseurl,str(page-1)+"&"+url)
        pager_list.append(prev)
    
    
        if begin_two:
            prev_two = "<li><a class='act_post' href='%s?page_id=%s'>...</a></li>"%(baseurl,str(page-begin_two)+"&"+url)
            pager_list.append(prev_two)
    
    
        temp = ''
        for i in range(begin+1,end+1):
            if i == page:
                temp = "<li class='disabled'><a   class='list-group-item active'>%d</a></li>"%(i)
            else:
                temp = "<li><a class='act_post' href='%s?page_id=%s'>%d</a></li>"%(baseurl,str(i)+"&"+url,i)
            pager_list.append(temp)
    
    
        if end_two:
            
            next_two = "<li><a class='act_post' href='%s?page_id=%s'>...</a></li>"%(baseurl,str(page+ end_two)+"&"+url)
            pager_list.append(next_two)
    
    
        if page >= totalpage:
            next = "<li class='disabled'><a   aria-label='Next'><span aria-hidden='true'>下一页</span></a></li>"
        else:
            next = "<li><a class='act_post'  href='%s?page_id=%s'aria-label='Next'><span aria-hidden='true'>下一页</span></a></li>"%(baseurl,str(page+1)+"&"+url)
        pager_list.append(next)
    
    
    
        if page >= totalpage:
            last = "<li class='disabled'><a   >末页</a></li>"
        else:
            last = "<li><a class='act_post' href='%s?page_id=%s'>末页</a></li>"%(baseurl,str(totalpage)+"&"+url)
    
        pager_list.append(last)
    
    
        cs='''
    
    		  </ul>
    		</nav>
    
        '''
    
        pager_list.append(cs)


    result = ''.join(pager_list)

    #page_string = make_safe(result)


    return result
