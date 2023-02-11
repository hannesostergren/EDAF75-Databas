4. 
    (a) Movies (Movie_ID), Theater (Name) and Users (User name) have natural keys.
    (b) Movie IDs shouldn't change unless a different method of identifying movies is needed, in which case all movie IDs would be updated. Theaters could however change names. Usernames may change, therefore when this happens, we have to check the records in the database so that there are no duplicate usernames. 
    (c) Movie screenings cannot be uniquely identified and are therefore represented as a weak entity. A ticket is also a weak entity and has to use multiple fields from other databases to be uniquely identified. 
    (d) We want an invented key in the Ticket entity to verify it's validity. 

6.
We can keep track of the number of seats available for each screening using two different methods:
    (a) Each screening entry has an INT column indicating the maximum number of seats. When a customer buys a ticket, the ticket information is added to the ticket table, and the screening INT is decreased by one. Using this approach, we only have to keep track of the purchased ticket in the ticket table. However, we have to edit two tables each time a ticket is bought, which means we lock the editing of both tables, potentially slowing down the purchasing process. 
    (b) Another way is to once again use an INT column in the screening table. But then directly creating that many ticket entries in the ticket table. When a customer buys a ticket, the username foreign key is added to the ticket entry, linking them together. This has the downside of potentially overflowing the database if we do not delete rows of unpurchased tickets after a while, which has to be done in the right way to keep statistics and information about the screening. On the upside, we only have to edit one table when a ticket is bought. 
