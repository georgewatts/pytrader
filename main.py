#!/usr/bin/python

import wx

import traceback
from threading import *

from igbroker import IGBroker
from lightstreamer import LSClient, Subscription

node_dictionary        = {}
list_dictionary        = {}
market_dictionary      = {}
merge_sub_dictionary   = {}
live_market_dictionary = {}
live_data = []

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(900, 700))

        self.broker = IGBroker(username, password)

        self.__lightstreamer_connect()
        self.InitUI()
        self.SetMinSize((900, 700))
        self.__init_tree()
        self.Centre()
        self.Show()

    def InitUI(self):
        base_panel = wx.Panel(self)

        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        edit_menu = wx.Menu()
        quit = file_menu.Append(1, 'Quit', 'Quit Application')
        # file_menu.AppendSeparator()
        # file_menu.Append(wx.ID_EXIT, '&Quit', 'Quit application')
        menu_bar.Append(file_menu, '&File')
        menu_bar.Append(edit_menu, '&Edit')
        self.SetMenuBar(menu_bar)

        #wx.BoxSizer(integer orient)
        box   = wx.BoxSizer(wx.VERTICAL)
        tabPanel = wx.Notebook(base_panel)

        tabPanel.AddPage(self.__init_browse_markets(tabPanel), "Browse Markets")
        tabPanel.AddPage(self.__init_selected_markets(tabPanel), "Live Markets")

        #Add(wx.Window window, integer proportion=0, integer flag = 0, integer border = 0)
        box.Add(tabPanel, 1, wx.EXPAND | wx.ALL, 10)

        base_panel.SetSizer(box)

        # Event Bindings
        self.Bind(wx.EVT_BUTTON, self.CopyLeft,  self.buttonleft)
        self.Bind(wx.EVT_BUTTON, self.CopyRight, self.buttonright)
        self.Bind(wx.EVT_BUTTON, self.LiveMarkets, self.update_list)
        self.Bind(wx.EVT_BUTTON, self.ClearSelected, self.buttonclear)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnMarketClick, self.tree)
        self.Bind(wx.EVT_MENU, self.OnQuit, quit)

# GUI Init
    def __init_browse_markets(self, tab_panel):
        tab = wx.Panel(tab_panel)

        self.tree = wx.TreeCtrl(tab)

        self.list = wx.ListCtrl(tab, style=wx.LC_REPORT)
        self.list.InsertColumn(0, 'Name', width=390)
        self.list_index = 0

        self.buttonleft  = wx.Button(tab, label="<<",    size=(55, 28))
        self.buttonright = wx.Button(tab, label=">>",    size=(55, 28))
        self.buttonclear = wx.Button(tab, label="Clear", size=(55, 28))

        tab_sizer = wx.BoxSizer(wx.VERTICAL)

        markets_sizer = wx.BoxSizer(wx.HORIZONTAL)

        markets_sizer.Add(self.tree, 1, wx.EXPAND | wx.ALL, 5)

        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        buttons_sizer.Add(self.buttonright, 0, wx.EXPAND | wx.ALL, 1)
        buttons_sizer.Add(self.buttonleft,  0, wx.EXPAND | wx.ALL, 1)
        buttons_sizer.Add(self.buttonclear, 0, wx.EXPAND | wx.ALL, 1)

        markets_sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        markets_sizer.Add(self.list, 1, wx.EXPAND | wx.ALL, 5)

        tab_sizer.Add(markets_sizer, 1, wx.EXPAND)

        self.update_list = wx.Button(tab, label="Update Live Markets")

        tab_sizer.Add(self.update_list, 0, wx.ALIGN_RIGHT | wx.ALL, 2)

        tab.SetSizer(tab_sizer)

        return tab

    def __init_selected_markets(self, tab_panel):
        tab = wx.Panel(tab_panel)

        self.live_market_index = 0

        self.market_list = wx.ListCtrl(tab, style=wx.LC_REPORT)
        self.market_list.InsertColumn(0, 'Market',   width=100)
        self.market_list.InsertColumn(1, 'Buy',      width=100)
        self.market_list.InsertColumn(2, 'Sell',     width=100)
        self.market_list.InsertColumn(3, 'Change',   width=100)
        self.market_list.InsertColumn(4, 'Change %', width=100)
        self.market_list.InsertColumn(5, 'Update',   width=100)
        self.market_list.InsertColumn(6, 'High',     width=100)
        self.market_list.InsertColumn(7, 'Low',      width=100)

        tab_sizer = wx.BoxSizer(wx.VERTICAL)

        tab_sizer.Add(self.market_list, 1, wx.EXPAND | wx.ALL, 5)

        tab.SetSizer(tab_sizer)

        return tab

# Non GUI Functions
    def __lightstreamer_connect(self):
        if self.broker.valid:
            lightstream_details = self.broker.get_lightstream_details()

            endpoint = lightstream_details['lightstreamerEndpoint']
            clientId = lightstream_details['clientId']
            password = lightstream_details['password']

            self.ls_client = LSClient(endpoint, adapter_set="", user=clientId, password=password)

            try:
                self.ls_client.connect()
            except Exception as e:
                print ("Unable to connect to Lightstreamer Server")
                print (traceback.format_exc())
                sys.exit(1)

    def __create_merge_sub(self, epic, name):
        if(epic not in merge_sub_dictionary):
            market = 'MARKET:' + epic
            merge_sub = Subscription(
                                        mode="MERGE",
                                        items=[market],
                                        fields=["BID", "OFFER", "HIGH", "LOW", "CHANGE", "UPDATE_TIME", "CHANGE_PCT"]
                                    )
            thread = ListenerThread(parent=self)
            merge_sub.addlistener(thread.listen)
            sub_key = self.ls_client.subscribe(merge_sub)
            merge_sub_dictionary[epic] = {'sub_key' : sub_key, 'name' : name, 'subscription' : merge_sub}

# GUI Functions
    def __init_tree(self):
        self.tree_root = self.tree.AddRoot('Markets')
        self.__populate_tree_member(self.tree_root, 0)

    def __populate_tree_member(self, tree_member_id, market_id):
        if self.broker.valid:
            markets = self.broker.browse_markets(market_id)
            if(markets['markets'] == None):
                for node in markets['nodes']:
                    member = self.tree.AppendItem(tree_member_id, node['name'])
                    self.tree.AppendItem(self.tree.GetLastChild(tree_member_id), '')
                    node_dictionary[node['name']] = {'market_id' : node['id'], 'tree_child_id' : member}
            elif(markets['nodes'] == None):
                for market in markets['markets']:
                    member = self.tree.AppendItem(tree_member_id, market['instrumentName'])
                    market_dictionary[market['instrumentName']] = {'epic' : market['epic'], 'tree_child_id' : member}
        else:
            self.tree.AppendItem(self.tree_root, "ERROR: Could not load markets.")

    #TODO Add limit dialog for 40 subscriptions
    def __list_add(self, name, epic):
        if(epic not in list_dictionary.values()):
            self.list.InsertStringItem(self.list_index, name)
            list_dictionary[name] = epic
            self.list_index += 1

    def __list_del(self, items):
        items.reverse()
        for item in items:
            if(item != -1):
                del list_dictionary[self.list.GetItemText(item)]
                self.list.DeleteItem(item)

    def __update_market_selection(self):
        if self.broker.valid:
            for i in xrange(self.list.GetItemCount()):
                # Get epic from dictionary and create subscription to it
                epic = list_dictionary[self.list.GetItemText(i)]
                self.market_list.InsertStringItem(self.live_market_index, self.list.GetItemText(i))
                live_market_dictionary[epic] = {'index' : self.live_market_index}
                self.live_market_index += 1
                self.__create_merge_sub(epic, self.list.GetItemText(i))

    def update_market_prices(self, row, data):
        self.market_list.SetStringItem(row, 1, data['values']['BID'])
        self.market_list.SetStringItem(row, 2, data['values']['OFFER'])
        self.market_list.SetStringItem(row, 3, data['values']['CHANGE'])
        self.market_list.SetStringItem(row, 4, data['values']['CHANGE_PCT'])
        self.market_list.SetStringItem(row, 5, data['values']['UPDATE_TIME'])
        self.market_list.SetStringItem(row, 6, data['values']['HIGH'])
        self.market_list.SetStringItem(row, 7, data['values']['LOW'])

# GUI events
    def OnQuit(self, event):
        self.Close()

    def OnMarketClick(self, event):
        item = event.GetItem()
        # Get text of tree member child
        item_child       = self.tree.GetLastChild(item)
        item_child_name  = self.tree.GetItemText(item_child)
        # Check if child member blank
        if(item_child_name == ''):
            self.tree.DeleteChildren(item)
            tree_member = node_dictionary.get(self.tree.GetItemText(item))
            self.__populate_tree_member(tree_member['tree_child_id'], tree_member['market_id'])
        else:
            pass

    def CopyRight(self, event):
        selected_item = self.tree.GetSelection()
        if(self.tree.ItemHasChildren(selected_item) == False):
            selected_name = self.tree.GetItemText(selected_item)
            self.__list_add(selected_name, market_dictionary[selected_name]['epic'])

    def CopyLeft(self, event):
        selected_items = []
        item = self.list.GetFirstSelected()
        while item != -1:
            selected_items.append(item)
            item = self.list.GetNextSelected(item)
        self.__list_del(selected_items)

    def LiveMarkets(self, event):
        self.__update_market_selection()

    def ClearSelected(self, event):
        pass

# Thread class that listens to Lightstreamer Subscription
class ListenerThread(Thread):
    def __init__(self, parent):
        self.parent = parent
        Thread.__init__(self)
        # super(ListenerThread, self).__init__()

        self.setDaemon(1)
        self.want_abort = False
        self.first_pass = True

        self.start()

    def listen(self, data):
        if(self.first_pass):
            epic = data['name'].split(':')[1]
            self.market_list_index = live_market_dictionary[epic]['index']
            self.first_pass = False
        # wx.CallAfter(self.parent.__update_market_prices, index=self.market_list_index, data=data)
        wx.CallAfter(lambda: self.parent.update_market_prices(row=self.market_list_index, data=data))

    def abort(self):
        # Method for use by main thread to signal an abort
        self.want_abort = True

if __name__ == '__main__':
    app = wx.App()
    MyFrame(None, title="Trader")
    try:
        app.MainLoop()
    except:
        show_error()
