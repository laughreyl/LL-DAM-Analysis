function data=fly_histo_3hr_new(file)
    
% Reads a DAM data file
% verifies interval between measurement
% concatenates inter-activity intervals for a single fly 
% generates IAI histogram
% generates activity histogram
% 
[x y]=size(file);
data=zeros(x,y);
for j = 1:y
    i=1;ii=0;
    while i<(x+1)   
        for ii= i:x
            if file(ii,j)==0            
                data(i,j)= data(i,j)+1;
            else

               %data(ii)=NaN;
                break;
            end
        end 

        if (data(i,j)>0)
            i=i+data(i,j);
        else
            i=i+1;
        end
        
    end        
end 

for m=1:y
 for k= 1:x
     if data(k,m)==0 
         data(k,m)= nan; 
     end
 end
end
% inter-activity interval: number of consecutive measurement intervals that recorded no
% activity 


% data.h= zeros(x*y,1);
% data.h(:)=nan;
% k=1;
% for j=1:y
%     for i=1:x
%         if data(i,j)~=nan
%             data.h(k)=data(i,j);
%             k=k+1;
%         end
%     end
% end
% 
% data.ah= zeros(x*y,1);
% data.ah(:)=nan;
% k=1;
% for j=1:y
%     for i=1:x
%         if file(i,j)~=0
%             data.ah(k)=file(i,j);
%             k=k+1;
%         end
%     end
% end

