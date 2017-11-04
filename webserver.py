from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/delete"):
                restaurantID = self.path.split("/")[2]
                restaurantById = session.query(Restaurant).filter_by(id = restaurantID).one()
                if restaurantById != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1> Are you sure you want to delete " + restaurantById.name + "?</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % restaurantID
                    output += "<input type='submit' value='Delete'>"
                    output += "</form></body></html>"
                self.wfile.write(output)
                return
                
            if self.path.endswith("/restaurants"):
                # make a query call to the database
                restaurants = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1><a href='/restaurants/new'>Make a New Restaurant here</a></h1>"

                for restaurant in restaurants:
                    output += "<p> %s </br>" % restaurant.name
                    output += "<a href='/restaurants/" + str(restaurant.id) + "/edit'>Edit</a>"
                    output += "</br>"
                    output += "<a href='/restaurants/" + str(restaurant.id) +"/delete'>Delete</a></p>"
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                output += "<input name='newRestaurantName' placeholder='New Restaurant Name' type='text'>"
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/edit"):
                restaurantID = self.path.split("/")[2]
                restaurantById = session.query(Restaurant).filter_by(id = restaurantID).one()
                if restaurantById != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>" + restaurantById.name + "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % restaurantID
                    output += "<input name='newRestaurantName' placeholder='%s' type='text'>" % restaurantById.name
                    output += "<input type='submit' value='Rename'>"
                    output += "</form></body></html>"
                self.wfile.write(output)
                return
                

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

            
    def do_POST(self):
        try:
            if self.path.endswith("/delete"):
                restaurantID = self.path.split("/")[2]
                restaurantById = session.query(Restaurant).filter_by(id=restaurantID).one()
                if restaurantById != []:
                    session.delete(restaurantById)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurantID = self.path.split("/")[2]
                    restaurantById = session.query(Restaurant).filter_by(id=restaurantID).one()
                    if restaurantById != []:
                        restaurantById.name = messagecontent[0]
                        session.add(restaurantById)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

                
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurant = Restaurant(name = messagecontent[0])
                    session.add(restaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
        except:
            pass
            

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
