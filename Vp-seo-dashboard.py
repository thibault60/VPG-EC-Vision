import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="VP SEO Dashboard", page_icon="✈️", layout="wide")

# ── Bannière Primelis ──
_BANNER_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wgARCAC/BGgDASIAAhEBAxEB/8QAHAABAQACAwEBAAAAAAAAAAAAAAEGBwIFCAQD/8QAGQEBAQEBAQEAAAAAAAAAAAAAAAECBAMF/9oADAMBAAIQAxAAAAHRyukAAUAAAAFLFEtJFEUSWnFyixRAgAACUQAEUQEnKEEJRAARYAJRxWACUQARAJUcVglEAlgA2Br+az3PS8uOalkoCUkC5tjvVt54rPPQJFigiWKIJUkc/rt+GWSJUsCcVgCRc12wrOt65H9XPjP5/wBPz+Rv7PS/lzLurOI8eU47Ad+OjQoAAAUstJKAAAACWCoUAEUSchxUsCAARRAJRAScoQQlEABFgSiUcQARYBCUcbz2ZrGsOPoTz5rMHl6xYAQARxWAEACSUAScuMAJRAJSwGQbh8+/b0Z9cebN6eYe3PzSvk7gidz82x+hx+bc2m/oNXj45LB6U815D1Zx6ZFsPOtNPU3mjd+CWceYDv6dGgABVlpAAEstoACiKSKIpYAAAJB3NnSvt+NeKpYEASiASiAk5QghLAACAAk5QgAIBz4I2pnnm+9HP6R82bh08cVnN0JRAJYBEnKVBCWACWICpZJAoJAAsAEZzglm4HnYLEsjaeC/D8fug8AEB2mY66er1j5N2jq3rtHzswHfjo0AqkoSglWikUgAAKAAACAJRFiuz6xZ6Y+nWnzfX88J6g+R6SVlAAJRAJRAScpEBFgAlEABxWACUcu96D0Zl567fpNmGt/mspZsiNa9tdpGJYHnWInxAn0fPscwnrdoawju+n3R80ad7ztdwnmoUCTuer9IS+agklgub9FHTcNk62ULEveL0Tvfqj4vyznKI0OKixE/XLpcLoklgCQKCcuD7bfiZPjFQZnfrPfSqCFlWgKIACgACkURRFEAAACJRk+L2aSpmqSSchxWACUQCUQglkAQAEWCUOPKEABN/wCgN/5aAzvBM7Mn6nLNIRtz4Mt6aNW7/wDPW5DrNZ5/zr5/yyKxiPfZBq073WGz9X1sDY2udhxrPZetdkRr7K8Gz+tVbl1htCOr7bz16fTWPS5kXp+M7ZNj+ftu6SjK826TJ1x3Den2HXz5FeUaTvwfjp6h85dnufL59J7hwMzXp8c2wmE5FrHL1x/u85whMezTqaZlh2aeeDO9bb+0CPu+FZvDbfjTa319frqPYmu+CByzvqvRoALRQEBQCiUAAAFgAAAiiAABEogUJEsIABKICLBKOKyEsAEogCUksAG/tA5LljOe9phhtrR2x8SjcXTfH1UYTuPW2U0+fr+kMxwTYmGm3dX/AGo7rTe3NR1nuYY7iMd5sbSOzj6vj+L54/LOMY+g1B6F0JtezJsbxz8pfg63Z+tk3PqrMsQXK8kwLuZNdbDwjvbcgwzZX2x5yzzjj1fJubpMUj8dy+cdlmLZN0vcGRfZqDbad551yjOToOzxHuDZnnvauCG1tAbW1SAj6Pni970RoGJkA6NCW0qDvrOhehOv686LZNjXN6SmICgFgKRRFEAAAABFEAAlJJShJJyhAARYAQDjykQEWAEWADjyhAAQARARZEAlgBFginEQBAAkCpUnFYoJPp+eLuvH9aI7jpeXGqI37or5oBEFiWQlhAFhAAkAEZATo3S0CAuZbh1NjXdj4fxOLYQAWkUAAEChFEnIcVEAAlJAoCUkItEknKEABAJYJRxWQlgAlD9vw2lrz1a9jYt78nmB+n583eBFgEJYSyxJYJRDsbOumyep9Zhd7Tq/HUlgEQAJABElgAligncfNtf45cA6PamGmO8fYHXx5PZLsI0xM++dMJmbYgv4M+7hNTvRulDHWW4kkCgkAEd/Tp3QgKoWAAWkoABQAAAAAQBJyHFYAJSQKAliAoSSWKCJYAQEnKEEQAEB6U1D++Be/HmW2vOezVzvTHoryprz4yubvgEqIQTlxgCAz/0n463v9Lm1/ro4OhLxxQhLAARPo+fau5ezy8i8fR/nPx1wHhtLBkOPDcv3fH1Obl2o8vwOvV+F671hHqrEOhx49C4z0GEybSyPQvfLs3ljOHptXCvl6xc68y+gPP8AZFgCQARkFOnQKKAAKoAFCkoAAAAARRABCUcVgAlJAoJFihJJyhAAQCWCUcRCWACWADPsB56xkGNEoTUAEQCWRARYfZw+ZZBKlhBCWACWI9NeZdgdPn8uEHPuDNAgFhUBLIgEpIJYEksAE57h9Mad47+0DqOPKePoCZCOjQLQgKqkoBSgAFhRFEUsUkWAQCxYAJUcVgAlgAlJAsVJJYoIl7WzqW6+fTnSDOMG8NpZ5gIBKJKAOKwAgAiLBKjiBLACASjiISiASkiVUskgUEgAWASo4rEAgiAceXEc+CtyZ15hdPh6U81bg0/anLIub1xsZZCOjaygAoqClKAILQKCAAAAJSwIEsWEpEnKEA2TrZvHoPG+6xz6k1b+R8jcWKEknKEAlHZ+nfJ22e7GvOos4tuPKRBEABAEpJYAJYBCWARJYJRAJz/Wz5xmyWAEACQKEkligiWALFgESWAECOPKQlhAJYc8ixzMvWby6XWWzvrzziPh3//EADEQAAICAgEBBQgCAQUBAAAAAAQFAwYBAgcAFCAwNlAREhMVNTdAYBAiFiEjMTRwM//aAAgBAQABBQL9bqNiynLdRfBb+DUnPylo1z7Wf5mMe9lbTWB/REfwZ+oDSBc5b4OqP6/ttnbPhe32+PpptJsUFODv4aVMvM6TgJRMEbYji329/f8Ahc47Mk/d1SfLTcCggx9CrxgdbeR2mwd0JMawyFx8XLm0V0RCD3dHPbqX+q6abSbJ6GYd0/Qgo616JAaQLmuNMnISZ9iiO4EdKvlD5CKi6Ru4Xo3IBnxm3dDbbDKwK+eyyDx5vt0DVli7o+ftR36hr7PeU2xeo1W3sRgZyDJ7iH0VG47Cp7/HxnwmTozt7XvCtCwegryxgkfF4gR+kipzDYSAiBPSdds6bWdv83q3pohUgRHgsXHx6X6SuYzqyEtggeQlrwttGsw0xnoemm0m3+PNepx5RZf8eaZ632li1/jXTO+elyoprLtSG3Zv+O5APKTIevIVk9RomU8cke0O+MZ2zugZ6a93KY3Vf3ttc6Z74CQ9pg9Qar2/A97Pu+lUGH2k22wdq39Exn2ZRnE54y332k2Cama0jOc7Z/ij2UesntzdWLSxjYTUiqWyerFHFdtN/mhtCgrDyT5u647cyLOuUwcDWWowYlecoHTSqu5HJtDI8OnZcV9yev8AZaklO0WNrzZR7Oy7iZIW+MdJCkB1YV6un17Pn0sWz3d5xr3I49pZLWjxXmPhiAznSNq+Qlh9IDb5XqPRkX2t6E8mUOrLX8+MJq0TdK8BCootZX2EubMQLe8Mh40NQwtsTpqJiF04Xh1CCxIhvkSCvQSrKa0AJsvJPm7pH/pWrxrhxTFXtEr3IP8AuVWpVXNimq/yV84ZLtVzqWkKoay4jq5tSN+0NOhXyxk5HsDNz8srR9oSDV0+4Not6SqDDeN7wkERPhqItnqKAysTnXJFpXXwqEVPVa1r8+rzJmU2JUsN1LK0V2C8ARkkL+hwUxlJXEx6sCkK53bK8ajOc1+aJBeuTGI8Fgqdb0cdV/CqztFVbgnsVor6aqOIqypudcTl1kU2/VyKtPP4DEyZMnp63ocaIWLkWX2nfp6L7W9CeTOIvq5W2dyrF9r+J/MLX6pfvK/GHmxOJqbyXeQQCrMydJ4KHc8fL6JTvNPJPm7pV/Wo1vXLvjhpt2St3b+1FX2ktYjoCAsKx3PzU8k204r6GAjY8W8hrMqoOJxtZbI5XLCnF3dqz01w+2yL63yr5qi2zrw+g+vcq+arHNhnxtxPnAe88nxZukFiMrhltXh26u8VlxkbV0DAljq1kyjsdmo8TSOvTyFW/lXzYpFh14prOiNI61Pgacl8qbZ2t1Gz7vHQX/d5i+t9yhNcwHXyX3336fVMZP496j1+BSuIvq5H/wB7F9r+J/MLX6pfvK/GHmwFhqr5E5NC3GtEC/XdRcNPmfH9GG3Ktd9X7GWfoH+tN4pN+E7u08cthtn9uOagt0ArnHXaGVytgO8zx99rejvtDVpNLjUuMi8LbVbAdl1jnW9nU3D7bDLdldh5V81afZ9B9e5V81KAi6wgZvjyAuqMLEdaDg5F5lFI+BVau0+TP+RgYEuqVNu6kolhJSvGg0YnKvIK/dpfU8fznjGKLaeVSDqsvnKfm+j/AG5C/wC7zF9c7g8+4pDw/DNp+noX5VdNKe10yRu4kbS1W3DVfBpi8gw27AHJKvaxKxIWyWFMHdyBdrqtZRa1M8ZCNCxb0OWtfP8ADXWs3HKUSW1DgS2q9RvxeobKqhTqm26VtGTFucdd17BNWrlGnB1uGi0uzXSB9sXdV5qPG0XaZrwBMgrNlFrZ7+xCtjZb2ucQPHUjstXfR4UI9ii3d2a0hWUnF4AxX1LMFaztNnFtM2lmZUVPX+SCWzS7KIklkTtJErNxZktimYWDJAHV9ZbGM6tYc1lrs7TCn7NSd2jfkeE+Gt2QqsnE3VTFugcDqWNqswdmnUXoJOlEPWjMrXcRLV+9DTdmJtGolxnTCiVw1w0mdMv5gnqf+NEkblk/lK2266QNcjejk0cLfp2ojUTf+FVL4nzx+50UDTS7zy+t6652zJBJDn0xWoMdEyATxnt0paOb86qkxLpWLCVmX67XbrIB1EOuZwPVCNeDvnG2/wCACLoZNvQmWuJae2i6JVGB6/iqLW3q+ujhquKsJRF6a1zXG9guVqHqh6gpRyMHpXGMw1YTm1uxGpjnrzWlO9wA6W6YB/Bk+LmhPsC8awa725VJoJe4FZbtm3qjVFH+oULXA1ctVg2enJPk8+deP1U2m3HAHT4EZaw8av20hRnbHVvf/MifCxj25kHlh8FM4ylIstmxY4TLlu0q1Qucic2teYrvFWd2GlurlUAqLPdZxxQXZry50nzTx5amTqxobYyO5ERrYJORIse42h2Am5PqP3HozwJfO0WOAax+oGv/AHK9/FEYk6OLY9wkW5znbPjAx/GNvFg7FB4lbuewWMqFbGNzWkYAe/szv3qdblqMr54CnsPIbWF2zTl6ANr7ZBbMy6XWsMWjUl4PXXtdvS9U6o1hGrbpG/GXXPF77DcsPKTGQruI8d1RXUBbbqvbgV+plqr6VJ+p0jfWJ7YHOztl44ZHZCySJC5/FpemodZtFh2eGeBnPtz7fwvdz7v6frJtp6A4f+8p/KxrnbNf4+lJ65ABhBS/+E64xnZG7r6HAXIC80zkjT3kXr6/AW8o9IXlxbUEbqwoxkun6SW8+d0vrGPbkpAWCu9OSMFZWCKWsl6Jo8MesuuukvhgMyVkuxWsYTVhuzN/Sdd9tcJ6+Y73SVMNLjkHHtSen0mSWRVcHmc7+LcGucDega6522nH3G39I1z7u2lxbRRiXVnEXd99SK31/8QAJhEAAgEBBwUAAwAAAAAAAAAAAQIRAAMSICEwQFAEECIxYEFCYf/aAAgBAwEBPwHjSLwg4oznWJilYHseKZgvukcWgkbI0uM9o2sxtWsFarAXVjeHa+6UQcvuBR+NVp+H/bfuWUSomh1YJi7pBgfXO2Vl5m0arZWALK1dMXbyY6DjyEYy932KVr3LOt5StABRA0I/ONxeyoCMtVmCjOla8J4EODwpsVOZqzECNyyzSf3GffDGh2//xAAqEQACAQIEBgEEAwAAAAAAAAABAgMAEQQSMUAQEyAhMFBBIjJRYRQzYP/aAAgBAgEBPwH1qsUNxR7npLnLl8FvnqVSxsKhwanu54QTcu49UqFtKdDGbHZRyRp9y3rFuDGoX54xiM/2G1SxQxw5k4wS8u/7pMPJJ9oqbDmAAsddqBfTarMy1OczX2ZYsAPx0GS8Yj6FldPtNYyXmsLfja6aUswEWd6Jub7I+AbYXNMpQ2balidmaPD46NaFHp/fnFYbEIGCBbVijeZvUHh87zSmOY3PSP3X8VyLrTKUNj/hkl5UXbU79QDrRg+b+LlSfiiCNfeO/wBIUVGwvZhU2Vew8GHmyKS1SOZGzHqSASj6WqSIxGx9spsb0Tfv54HEZLGmYubnyojSGy1InLbL6EYaQ6U6GM5W9IuIZOwrEMGbMKCk6bhWym9EQ8vmMvXh5eWrGiSTc+lTJf66EkbwOIxa3D//xABREAACAQIDAwUIDgYIBQUAAAABAgMEEQAFEhMhMSJBUWFxEBQjMlJzscEGFSAwQlBgYnKBkaGy0TNAdKLC8CQ0Q4KSs8PhU3CDk6MWJTXS8f/aAAgBAQAGPwL5N7GVv6JKd/zT04rEHDatbsv70us2gm5D9XXir863p/XbDecXdO9o/Kl/LEiA6tLEX7ngZ5IvoMRiWsB5ewYN9K1vlBcm5/Wgqgsx5hhVqImhZhqCtxt74Grc0iph/wAMeN9p3YHeBp5H8sOHbDseAF8Fuk37uY0LcJrMnbcX/nq+XFhU08HnZLH7MBp5mquzkri0ECRfRGKroTkD6vdeAppH+dbd9uL1MyQL0LyjiHZs8k8j+Mx5vdT1OrwghaN/pWt8lgqgsx4AYWSqPekXQfHP1Yq9hD4Q6RtH3t4w+JbwzyRH5jEYjqJW1OgIkbsxLM3jSMWPudpDp1fOQN6cAVFPHMvzOScNLErJpOkq2I4B4sKfef5Huq2iO9J7EdRBx4GmfT5bbhgGrqQo8iIevGpacOw+HLysTyjg7kj5IjUCV5wDbHgcq0NzvtLsfrtiKnMLwmQ2DMd18W8uVR6T8TZrTlvHjug6+Hr+73iaAndKl/rH8nFVON6s5t2c3u/AVMkXUrbsLtnSaO+/Uu+2KqZT/Z8kjr+KtrTwmZRx0G5GPDQSRfTW3xSGBsRvvjL5t2sy2cDygPi5ZojZ196o4Q3L17Juxf5X4qE0D6W5xzHtxbxJwOXGcM01PDpG8kqMOaSHZQjcOvr+JAqgsx3ADnx/8ZWf9hvywYponilHFHWxxcZbV/8AYb8sNTvqXS2+NuZu7ZQSeruFKWIyFRdjwCjrPNhp4oUqo1497yq/o9yEhjaVzwVBc4NPVRmKYWJU9xXjy+qdG3hlhYg4ZHUo67irCxGLDeTgs2W1aqN5Jgb8vdGuamdaQELtWFgT7uzAg9fvBNJRzTqPhIm77cAVlLLTX4bRLX/UdN+Txt8V1UvQoX+fswaOnbwS+Ow+EfiW444zOTbyGRHZVfVvA5P541MxZuk4zBBUSW75jXxt9iDcfcMEnee7PNUwtKsiaQU4riqqo49ikshcIObGTQQ8jvzw8xHw926/24keNNvDILPEWtfoOJ6gqEMrl9I4C59xRwQzFIZ5QsiczYq+xPw9zMJpJWNNEkd0J3AFwCfsxtwN1REG+sbvUMRSv+jpg1S/9wX9NsZPIsjIsylmVTYHcPcrIh0upuCObFLUVD7SZpBdumzke5hzWQMsk9Ts0B8jSd/2jFJVSR7ZIZAxTpxFPTQGJEj0Xfxm9yKaji2knE9CjpODS1iBJbatxuCMUVG5skj8rsG8+jFRSRs0FLTWjihQ2VRboxWRVDbSpo5YxqbeSpO71+5VEUs7GwUcTiOkBJfYIz38ojf75op4Wlb5oxA1SVDy3sim9rfFM0EO6ed+U3QtvifN/On+DuZh+1xfhbDGoqGkeNdRpQtv3sNTVtKc3qkNpSsmiNOodOKDOcsTYU9RYNDe9ri49Bxapqm1oNZpVS2ofSxNeBZoo5WGycm3HqxkUrZdDMssepY3LWj5K7hYjCUc2UU8aFGbVG733fXirpoF5KztGi/3rDFPTS00ddmki7SXak6Ih0AAjfigzuhj2ENRyJYb3CPv4dW7FRnGZahl8G4RpuaZujFJHJlcEF38C8RbUrc17nfir7E/D3PZC3zIR+/jJc1Xe6AIx7Rv+9cZtV8DLopUPabt9w+/Hsck6Yl/AMSyyybCgpxqml5+wYbLWylI4JAdlNtG2gt078VFFJJpSKYx7S191+OKbMRVGWG+1mqLaSU8lV7d2DVUKCjrkICxGS7nfz/Vii85/qNipkzWhjaghUs1USwN+ZeO/ENHlOWpSCR9KcpmY9u/C5fHQx5g0Nu+Zpy3KPOFsd2KGtpoxUZfVIJkhm/CcZTVzUEMwmZDsSSFTkHhbAjmmXLUlcBFjQuOzCUdNdIREl2bees4evirhIxOo1UilRGgPK5PTiDL3yiR1lYRiqll5RJ6hwxNSRMWh3Ol+NjzYGdZhF3zNUNopqckhe1rYzOLLY/a3NItMl6ViNqBew4/zuxt6yZp5rW1NimrI/GhcPbp6sJneTsGqNPhIvK6vpYmpyCqMRtoHHjaTexxNnEGURGrh3SRbR9IN+3o34DPRRVKSNbYEsAL9G/AybLqRaSKDfUThizG3ED0YWgqMnjSkmbZxy7Rtop5tW/HesdLHMDV7BHluTGNVrjrxJC+XQTyGFfDOzavuOKqsrGaPLaNdczLxb5ow2WSZdHQiZW73mhZi6EC/Kud+DldfVmlkWbZclNWs35ujBedGqIXUbCijex4C7O3bfDVmVUq5XVRPpYPISvXf6sRUUuXyV4Ztm1bJJp+sL0Y2NP/AFaVBIgPwea33d0RiSOL50raRgNUVaVj+RG9lwI4Y1iQfBUWxSR+TGT9p/2+SGb+dP8AB3Mw/a4vwtit8x68TMxuS5JOMn+mnobE3mD6Ris88/px7GfMD8C4i82/owY33qKyV/8ADqb1YqnnziOnk5I2RgdtO7pAx7T01aaypDAg7Jl+Hc8RjIqNNyvZz18m/wDFjLPPrir7E/D3M9PS0A/eOM1oeL0xLoP3vUcZTR8DKXq3+s6V+5fvx7G26EQf+PFXlcCx7KpN3e3K3ixGKOoqglNdWKxStaR93MvHGaefOMpUGwaQA/vdyhjmqUpIQ+p5ZOYbRsZZFSH/ANoMd49PAvzses4kkYXMUJK9vDFbLJn0Ss87sR3vIbb+zGU0dBUmpalGksYyu6w6cZB2x/5bYoPPp6cf9BPXh7eXb/y4y39pj/EMHzKYyeaHetMyxS2+CQLfz24zWumOimihGp/v9WJHtYMxNu4JqWSw+HEfFcdeP/UWXqI6iP8ArCc56b9Y9GMyyeffHVREgfcfuP3YlNSORluuaTtTh+9bC5hKDIrkibpseODnnselEgbwhhTnPSvX1Yy6aZtUr1kbMTznUMN5lMTCSpFElRJdpipb4Y6OzFPXTZ4siw3OhKaTfu7MQVVK2qCSsQqbWvwxICdyxIB9mPZCRuPhv8oYg84vpxRfs/8AEfcvRueRMLr1MMFfIjUev5IZ3Rx8qZWL6RxtYf8A1PcmLbu+KxdHXpU39OK3zHrxJ9I4yf6aehsTeYPpGKzzz+nHsZ8wPwLiLzb+jDVD7kFbIrHoBJHrxLKRyJ0V1bp3W9WKqtkYrodYox5THefuGMmrIuUIdIbq3afSMZeEF9Ems9gxm0oYKKeFJDfn8UevuZp86ohHpxUUbfo6mHh1j/a+J4oN0FKBTIOpRbGQN0aR+6cZj7IGjWSogulOGFwrbuV9+EqZGaVwrySO3Zb14z2qBASCoAI6dX/5jJvOj+PuUXnP9RsVORzv/S6Ya6dj0c35fXg083IaVGisfK6PuxmELCw2zMvYd4xS1b3D1DsEX5otv+2/2YyDtj/y2xlcbtqZzBL2arG2P+gnrw3nP9XGW/tMf4hg+ZTHtlNG1THXDRHRW1RuLeM/qx3psEoKO9zBTx6FY9fT3KOnmQPHIJFIYX/s2xPTSrpkicoRj2SmX9BsefhqKkfliiqz4iSWf6J3HFdPGw2ubOnJHMq72+06cVSRtpaGnecC3jW5sU0SOTT1Egjki5jfdfEaRbk79haw6TpJ9OIqRDpMqRrq6OvGYUER11FK5OkdTavzwkca6nc6QBznFHSo+0ENWiauk334m82nox7Iuyb/AChiDzi+nFF+z/xH3Mc0Zs6HUDiepHB7ej5Id8Ux47nRvFcYaofI5FqG3skdRpjJwhKJBDENMUEXioMO6Za09Q66WkNRYfZpwssVDLDFqvJH3xqv2HTuxDlb5O4pobaNNXv3f3MNMmWvPUMCpc1Nha/Rpw1R7WzIjlmeMVXOevRimpJMoeNaZdMJWq8XdbyMCp9r3qauxGvvjSLdmnD1FPRvSSSOXkvNrBJ6NwtiOhzzLvbJIvElDWfEMFPSpQ0MF9nAm/f0k85xNQ1VMK7LpfGiY8OzEftJQe16CRZHZnLvJY+LfmHVhoqegWlebTt5TvZ7cB2dyXLvaaRopXEjOazlah/cxFXUyb42JVHN93Rgz1cTTozFmRH0E/XY4gyyTJnFNBbRprN4t/cxVZdVUffeXTknZ6+Ut8QHKKIUNLHJtGjL6mm+k3qwiR5eKemMglnCsA8x7bYgyp8mkFNDYpas5V/8HXjUY22Gq+z177dF7YTJzkz96JwtV8q97+Rh6taCSaXeEvU2Cqebxd+O/qXL2y+t1hzIs+oE9NtPHEft1ky1tXEN00b6NXbgSsiwxIuiKCPxY16MRZbmWWLXiD9ESd3VfEmZ5hSNWTaxIipLs1W3NwPVgVMmWSQ1Fgupam4sD0ace03tM/en7XyuN/Ix309BJOqOHhj7406bdJ078bf2tenrLBA4qNQ/w6cQUErrNWyASLDIN1OnR29XNiChzOmp5qeoYR7k4E8MVVNBuh3Oq9FxwxBWwhWkhNwG4HHfNblc8NXazNTTCz9txhMvpIBRUCnUYw2ppD0sefuU8Ba/elOkR+la7YFYIRUDQUKE23HAr6HLZlqFbWkUso2SN9lzj2wZ71W122v517420OVpDmpj2XfRa+gc+nHfFPZww0yRNwcYary7IY6bMm/tne6xnpC8L4WtqaR62ZH2ieG0b+vcb4ap9rXpqsgLtBU6l3dWnE+Wx5O7w1AO1LVe83Fj8DG3OXyyQCxSE1PA9bad+Fkkyt4KlF0JItTcfWNPy6ilAvoYNbCZnQVkMc7IFlpKlxGwI6CdxxFmGY1UMjwHXHSUziRmbmuRuGJ62f8ASSte3R0D3FDPIqiupbM0KDlyv0N0g4lnkN3kYu3af1vei1FOfGhkFwcbWGmQeUq8krjwUksX13GFjFRtnO8jTa3/ACLgCMVBvqtzi2L+NM3iJhpJG1OxuSfjwAC5PMMWkjZD0MLfFuwo4Gnk6ubtw9HoMlQkhj0pvuQbYjhrI9lK8e00X4C5/L9fqqybxY47AdJJ/wBsPPKd54DoHx8tNXXnpeZuLJ+eFmSGCeNuDaAcSVNRRRgDgE5Oo9G7BIXSDzdH6js2qEpyeDSeLi6mGQfNfH9V1fRYYLTUssaj4TIbfq1AZ6dIMtlP6MQhS6jienGb5jlkSCk74ZmqjCDxfdyj24oJKOBpahqVVkRB4ramv9WMtDC4NTHcH6QxDTrlFPU7SPXqNl5+zFXTSZYlHVxrcMnN1g2+7ElRFSSS06MUMi9N7YpjX5Q1UZomKQjSzD51r+npxmRoctdNEvKgW3g8d+DL5NhbVzarfR4476goJHhtcHcCewc+Nloba306Lb74749rZNFr2uNX+HjiGOaMNyHurjqxnqjKTmI5VkiVeRv6DiaKho2Zy5OyTggv04ElbRtFGfhghh93yRMrnSrSM5J+z1Y5O6lj3Rjp68CLMVlhY8Jkbk/XgPHLMVPAq4PqxuqKgfWv5YemppXmEe5mbp9/WGS9RS+Rzr2dzvaE/wBGiPHy26fe7DeceEjdPpLb3nbpS09RKPFM66tOMkqO9knqk2iSU9jbVyeYYzXLaynipaiHRojjXSLCRbrbFHQ1VBBRUU43MiFW38GJPHGWftMf4hiH27mljqNnyAmrxb9QxUJkMck9TMPHYH6r3xW1qgNLG8jC/TuxDLXTmd1gcAkAWGPZT54elsVUNXUGWBo2cRngu8cMNRvOe8zJLEIPggKGt6MZ5Usq64ApS/MSN5wK1vZ3A/KuYN2zI6NO0xTz0EsUqy07GQwtcarHHsh7G/EMZzR1crUffLbqtPgcRx5uOK9aPN4c7y5hdy/KdF57bz8kaTLKdt2m8zDtvp7sNIJW72fUWjPDgcEof6TLyY+rrwSTcnn9/gTypAPvx3jA3h5Byz5K++rS13habgH4lPzGBL3rTyq28Oqjf9eJKiaExKvkOd56MHSLLzD3cEftWses6JKxpNTjr4cMZjNLliZhN31IVaWTkjlHmtihrIPEko1NvJOprjFHUyXMcMyu2njYHEE9IsiokWg7UW337lXk7rL31KTYhRp5uvC1lSHaIIy+DFzvxndXMk5jrJA0elRfn47+vElXVLI0bRFPBi54jHtrKJDTbWV7KOVZg1vTipzalRnpZ7B4n3Ei2PbJaKfvq+vYaTbV2Xth85qKfYwsGGzgUX4fecZrmcqTmnqgdAVRq4g79+MwosxpNvQVbFiyKNY7cVtDkUMzSVilXeS9hutz/JQSudKRxOxPRuw85uI+EanmX9QhntqMbBrYeaVtcjm5Y+/RyyNpUlpCTzC/+2LLdaWPxF6ev3m54/qd7bun5INpJGoWPxBSZZTN4JI12rD4R6P1uwFyeYYWbMbwxcRCPGPb0Yo46eJYo1ltpXs/5FC50jpxqSKoqKnnmdB92/diKn2cse0OkO9rYiPkzj0H5AaaxpUU/Di5vqwJIK6SVDzrbH9Zl+wYjCzvJM/wT0fIqVJTeqpmTVf4Qva/csN5wtZUJslZtIRvG+LxT5jSRK/NOBpv22xyFki+g/54Zlq2RRv5YwwRtag7mtx98108pQ845jjviUhVCa2OJJ35+A6B8imANgwsevFoEtHflSt4owHtt6n/AIr83ZhfPD1/GEmtyyrJpUHm3DBoITYD9KfV79T0CbuQrv6h8QgDicaJF0t8Ug2Bt04CR1CxoOCpEgHoxG81RtogeUmkC4wJF3qzIw7n/8QAKxABAAECBAUEAgMBAQAAAAAAAREAITFBUWEQIDBxgUCRobHB8FDR4WDx/9oACAEBAAE/IeeP+UmasPjf3oMKfOJPjneMXsqVto8H4mpJr9/leo8XouAKWAxai874C9sXvFDAomMTDE8Jg/8AuxQnZxGUy+fv0kVHVio/kXptSJQBLt01JVlc6esgMIBlaiCFGLiTGWDzvKAsNX3BD5qJ0mNPmbeKQ6Fp7FIlinFKpA8QDycD149LHRj/AIkMQmLSdsTQ7Ho5Pa/zRw+Wtj70qJlDahf5nmDBrs+9aj36MeB80vQ8wQC8B3OYby16PzJHzweDwerH8FHUfS2W6DlauEN4pD6efakotfqczK2lPO9R6L0AAJn9JU480xXO7xDXyE1LPB4gYpz+qMeKiUuafzHxShm28jE+1Kys5PM/HIeBKIdon2fRQSYsj52nM2Up939UoZ7mRvex7UZaC40W3/GvIy8yxIneGoZMEQvMUjRcg6B5wqH/APK/g5XpvReq8JB7yjjwOgteRx5fppNi5u23wDnatWpPZhRTAnvyEi9WH6/ZB+fTxUdGOirSUQEbkzSEM7v29U9dgSoDJoJDZkSP3PnovUeq9S4JkPch+Fp6NyhRdmTkPoI9DFRyLaLsOgzKcAJb7RqVDsCPQazQMLZF+bD0D6RD5gcq0DhGhsLJH3G9AhMbiVogFUkIWZMnLjsQoTwwNuLqiWHelTapskbL4pFIkJk8iLbhFHsUZlUQpJJhwOL0PDUQvT18ugaJRgFEAYtD0uCQNV5WNXLmQBhE4+OLxCWM6jhWQh6FmoihLpkpstmR7HP0LGku2J6MdCPTxxtnhr3Z/CsVyj2gbHonqvK0hIguJTndSblo5Yvelqli8rQsYMygiDpU5CjKuLxh4lsWmbTk/wBUGnJ7VoEpLB1RRqCNtqDLYzUYDDCX96RsH5oMHvxaxbEZBtX7rRwPksLTIGomjUJ263PxQfkzxhCH4DzTHFNoXueXlf2VjyMGnflHAYFhsHF4PgVRhk2b0GnU7IP3RWNIgSVvGR/fLJ2CRY1hkUGwEXiwRr4Sj5D2VTAFuIFwWvMzTlpJoJnLng8b8oZkGyjgBQyJLp0naed5Q7OxE0d3KmazcixMuGZ1Y9YubaHLybqvp3less1mXuQcYFzGxU7ntVZ2ZZmsUpGSikRCew+KlvKUQGNkYWxoJHmAgQXQ/NHq6NAt3IF9Kxo7gwnN022HV2BBQyGvNuEwYrz91MPZF50TeUsdqZRvtglyJSWhyeE9XkUDhhnX7rRwP7JV/VNN7QxLtF5qPvMT8WlH+sF6WVHLJE9yB7VbXDrcmXYqaBG9KqWsAYEO16uu/ahknYLC7P2pRuRFREC3G6T/ADhqIBQPthiCdAmh65TvJsAzsWjGhGXwpjkIBNb/ANyPUHQsKgilyhZYncriDbDzUhR2sWISyd1qY7pkyzLv2qxNnG0DE2Pe0Uv4a6lAsRJ0bVAYGRs52uVBAgcccYLgsdtbXoVHecupLzg40TxYzoGBtV2k5oDfyJPNW4bowxMRkMN7bUuUOkFgGzjpDUrjWQQS54kYvNQc4ZRLSJbErTfiYPC0WCF8qkYSWrCsZ2CJpyGM6fPYscWrUErRIxAJbtTSC7RYUTVj9konNjEQSgtHIvUa0EfAIWEsl1pUfKzADOAiAY7RFYfhwHDJ3TMUEd6AKsQ8JasxUoGS6UKqXdeE4zcLEo+/4oJoNAezL8VgYqhPUECIqKjhHCKio/lFmvwn1p8C0Zs8VKz9hr43bDwkUdUHyKNUxFVm1hv5qEwSFm60IkrKb+ZpL5lX6TWv3Wjg/wBb0qYG25lDuj5p4ZMmv5EfCv1iQ/qgMlpSQAXi4aZtGgQZAsnIbscAxGjupLj3D24O11PQM0Bi6FLz9yHqQRnvFFkl5kkl7Keaxjxix2kgxSvPYM1kMY4XP2+msehIyJa7cEb91vVgaVnG/TL2VD9o2Bd+nyoDYQ6JeDxlSZZZD85UQCNnIgHgM5+FCVLpnaHzJS3ujO7HzDQwjQxLKNxh8UwHZnMl0ZZ9+1LIx8yTV+83pMcRZgRF1yNO5QR1KMXdSxGvWIJhvjTyEI0LvtadBAISj9po5tXLtwv6En2KuV+i+/RxUdaPUvF9ERMN3lLLcBMPuXJMfGvhPrX6zXip2fsNfG7YokgmZ74upW5lihJQSkdFpgPZnyVhaUbJNewFY8oegStXrRuswTgUv/xX+KnJfTrvnyqN2yUL7jXdD9rtXY3IURmyPZqdBRpb3F7inQgbFJiPdyQKbhxTD6DdsK0jaWCjL3FK5vFm/wBCVNhzBZjfMPLgcKaqgRnLcmsfiGRv3W9JAwDIZB6RgL70Unco61KXJi8IyXhGQxsw0xJ4tRipyWwNAR3aT4gEH6MLUSaRl+X3VYyVgYPjM09I+ZgA0SS9FOJoz7UqvKHBIbz4Evioa8yRANtwJ2p8huLJYKkuwPIH2nieA/aaOaWND+iShbh4GgA/HoY/h31B89ntQSmT5NPAFvBUHssRpw1c3Or6Dy4mbTxlm0gtK9p5QPg1KvpgaEGe5q4UKlZAS6F5ypMGgt2kjAC9r47VipFHEBObA9qgpQXDWk33RL3aeE2ZydaI0KIm7uM7iTnNXMzHiY7Yxpc2rCM8f8UlBchwhLyjGr1ZGBOZQwN78Mt+AAgRwf7QkjFAAkm02camUapDLpL7VMfhaMEmcWLSS8PCACTF7Bpe9A6epYWhLxCwLEzRXDFNIuchN4acMaIgJvOLF70eRYJC/wCVGceKA1icKklO5akh4mpITlvbtUzGgeGyiUMzSHHBn2GBtc2otejIDgPfGo6DpZZNhMpiTKkKic9wQvAAC2GdEgd/SY7sKTOmNb/ec7HndQXGP0qS805GFXY22/HOGXExKl8pKXMJLq3WG9dvY9hYqJNa+bWEn2M+Irb2hsRHwtCYuWKMKEzRNthZPwFZ2xrMfW6fkljxSQZc/gzh00qVzmLECBAHKSsJ3SGSBjuVNwNziiYEzdjSc6V/HQY770D51JkabyQULTyWgszqnalvgvA1R5WxoZlOkPZLFSH3DqCOhbQVOkOChM4Oc8ynkfQR/MPReg8XpvVacEZqwYZis6/XkyAEb5VCQSU2pGN7uWFRuXwYCIDsAcmH0yJs5LqGcj2qZA41SXoPI9eBPNv3xODvQBlqlaINSSjpD5ifmiTCyJym9R1IqKjqR6V4vF9E9J53qvoX0jU9gVYEw1h/Ztnu7FKozpl6EdOPSvo2kbOgCVa3/OV887/DCMVENjqsA70Z2BOcoDW5UDojAqATvdwjkfUvX3eMgN7qmDPs5QfyTzPMQTBL/wCB+7Uaj5uD4ojMxPeSJFEKcoVQaX5HoPF4BbZSt26YVPFrjie5Ug2TNf5rEBcB7sOZ9BLLTY+EkSb2XGjbCW0RADZYqYez4O4csDLk0AwwCRKBiGRC4iJ6UTbUesrARniqPcsMkLEY4pTA0wLIkKEmEQxVMlRzisDlk4VM9xWJqJfSprTIIO4z4Fe9S+1GM1JHZN+XsiaFAAy8JmGp7XCpMMwIbFRtbfillWAwlpLlQELoqY88z05tGX/AHhenABFCmal+ae79VOaUfAkW70Wn5Fk70XjW6UtUiU7wjTmejfxOJ97+PqrE4VvbAbfgGXM8qEClgKdhXc6LNCBxuCQnehzLHVzhCSj32pnxNuMLyyfuFH0RKiUKGEkT/XC4i4CljJrZzUKBkaCTJRYJmAqKMh5L4L5ZrNw+4CAApQ9KZgaCUI2EMVEbeAlqO9t6f2gBYry2fdoEwyx4EDx80XfDEUGYwYDg7W/sWjdcjnsW00mgnf8AFDfHKSOZ68dKOMVHqnoPF6KNxJniof24xcygmxhNLhhWIADM2fj9xTkESpu8Hq2Dn5MULCwVi2Xd+urMjZeQt6A2fwKdlDMy0RyAOdJlGWRlDvyPFzKCCVx0NQfNZDsOtqJid2azR9cbmbjagEIYTArHtUfywKuOS600vmy8vVduy0pRcQKQWspQ8LJwBzhGCjoUg5FM00o3aj1iFkxlzoobtZHjeESSi6BjsEp8msEMhyYC4SYrRqAWwm0WZa1i8zFDhgkwcbOFQqsqCrMnBcDg+pjqR6t6L0S9qPgC5qLQ/HXnPpvF4OQQ14KM0vvXseR6QKHv2kE+0qaKhE/u7tPI8iMkq6tKQlmMNuo8jwzFfFlp/hY9K9B6TyFjBTzNPjqPF53oPCwZskZ8D74PoHi8xN1sBK1c2o/Qz57VHYeCMX74fyz0XmeL6F9C8j6R4vKTTreMxReOMQHZ/pQos0AVwm9bgP4/z6mOhHqnlywuifNF/FYHQpp9UHDz0ICSQCDU8r0XkfSvoXneLzzDbGsWOVXsHzh4IQKWAqMh+OJFlMsP4/C1aKbLEd6EmR3PyoYoqTQN21TDcLCGsdNqYbRBfumdAAhyBaWrDU49tOs/wTyPI8j0XlRnAI4JGHyHtVslhZ+XN2KtCl0Pgy+6ken09EfwTysz8cmJge9MoyTE5nZ1GirKZZ1t/p7cjzvoHi8QSlIDeksIykfrrvI9B6LyNY8hMCSgHvAIKOOvOLMwKUOVbazh98P/2gAMAwEAAgADAAAAEEAh/wD77/8Ay+jDDb2y/wD/AL58+6ADT4oQiQBDzzhAAhLb4o4AP+5JMKTbyQEgTvgFIL/+SMCJP+K977/aOIIMMNecMLJPr/67tIADT4oSAAgDzyiICtn6pIoLa7oNsHf3mFAD+/kMx777SsYf+f77rMINQM4AEUA4MAMajr/5trgjT44AQgDDywgDSjb4Y4LD46qcIb7wmAgL/wCpD+/uGSsDD+/jijQIZFB6SKilBJERWhf/APvzqAEvrBAAAPPKFpAFOJBiGgjAg1gn4ooRDpvIXol/6jzAPd6xkBoYQgx+jsgig4k0YZIs9/mggBHriBIEFPLCAkIOgLsrDDgIhzgc8hBmLpGfFVZL86yw8wgDBZh1rvvvrvvrui8wQQAx/wD4tqRDT6hAAhzwq4YICwiIg6DZJGp/RtQJrp5zX3W1UuYAMIRklPz/AO/37zz/AP8A/wD+6LGBSD3/APr5iEvoEIAFPLLACJvjggmPqrjwktvMHtAjPrSxv4hgQwxkIWwvP/8AtIMM+PNPv/78oIEYLP644RDS4BCYbzyRICpboECpz44usP8A8oB4qe6PaO1/bDLDmBbme/zjDAGOOOADDT3/AP8ApIUAJb584jD7iCilKvixATb6qsMT4J5MBX30EKDARM7crTMOkOELb7+MMAqIDgBAiIoMPf8A/fBAD3/uqEQ+OAEAE9sYEAC+yiAE++CXWO/tpAAU+5CC/wDh4UASR3/44wAgBRffDRQyDgA9/ngkQMlvjTh3qiEEANPOEIEvrhqkPugkylvvCQCEt6Z617GLTQ8rvu54AozXPffPfXDYIo9//wAauAPP7voBD7iQghzygIAJbrYkJa5oMIJbxEyAJbwlML76oMP/xAAiEQADAAICAwACAwAAAAAAAAAAAREQICExMEBBUXFhgfD/2gAIAQMBAT8Q2hDgpSlKU4IT3FsBKJLWFoLxISsa4TpreHRcwhCEJmnZPUT14PCOL4kMQxaI30xOXRiGJjEJYJNjjbouITFKUpS4hBpybgn+Dv06Tff7Y2ruvzIeiUwhi7HhibQ10hcTFLiEIQhCFKNJIxL10Oyk9x4ei1+5eHqkXExSEzSlLpDoURMX3VhD3e7HbDzdKckJpMXMLo/b++NDEPwNjqVSonjIx8eSFxNEP2nh+FDEPD0Q2JYlrz9bLxf0gOhQdr/v14W4qzsmrEMQ8LX7l4fluOTk5Lt1hiHjvxQSctufobGU5nwRupfPBBS8sSmqHtCWtQxH3V6/NmLwUpcTbrDEMQ/F/JHAsdS8EX8tvo9Ev5FKkGLZ4YsVznFMrwXEIQmLjrVY6z3huKnEoanqvRD1YhiGMWxtjrvj0ezZDopcUpDrHWiFKTaawYhiynGejV1q8PL2QxDEV8Ef3H//xAApEQEAAgEEAQIGAwEBAAAAAAABABExECAhQTBRYUBxgZHB4aHR8LHx/9oACAECAQE/EK+HrSvg2Gc5FYm1BeBsjuJakHG79AIJz/Yx941bUZs8I/euPPXmTxsInRuGE5q9puYbu43rf4xOKw5fx+9X+X5D8/qNSteBf989UZ6CfWuJzS164P5h0r6HiqVpcuXLlypWiKhcRGnwJCPhxKYMHsQaWKNr4Haxy4/tex/Tlf6/OzPp9eICcKP358FS5cqVK1qVKnMuCq8oTEXo9f8Adx2Xe8iQ8KqWkY8EWF3zo4isl81F5rVajOtDXqD4QtBbK7U7amJmV46mICDgxK8LM+DE0cqkttHJLpYLwzBZgTK45I93G+I8VOoIYnRMM6vTDUxPad6kMRA2lkOjbi7/AFf8yye//ONgS5XnrTPid4s4nL1CxMppKiNkq1heICCQGuZVjExKeZTxHqVkhcpJTRO57zJHmOuJ3CGgqEipmW9QiwC8qhZAnzjHOfAYmfAw8TtYbmOtdaMDR3OpFgacc+Rr2PWKrb8Dje6uqVKogUFbHaCtES7/AGitCo7WdbLZ1BjL0uXsNMQ8FSpUqVK8JHew2WYIOYkFbgYPnU2ossKr+okys622jm9EhRRv02hA9YmZWZUqVDUjM+DEucypU5ly5W9hudXZReiI1Z2Oy2q6jDb0BHHzil+WO1jupBce43O4w3BL8FTEzvxHYFtQewfciXIRnXgZ1tYb3azqG0oED5QnhQlmiwzvIwPFiZ2NUL+cIcjBjn6R5htRhxVHvHTcsYeBhtpzo7WO1nW/MvXt/wCzgyGPzp//xAAoEAEAAQQCAgICAwEBAQEAAAABEQAQITEgQVFhcYEwkaGx8MHh8UD/2gAIAQEAAT8QoORwHPq8NRUNQ1DUX64TySaTknis3Tgk1rinFJrvhE1EX3TmtN0ng4eCQ+r7owqYXIsAeDqHWcoVEYrMZFJ+0Wclpruwu5DpKkfrky+VDPZMmjXAZ4JJabOa1XdTQuLpngmbJfcDlHQBulzXMNN6dvgPddCx0KYOpiaGM0OJcypuexShODGMBDWqHgVu4RxiSo5TeLic3hBchvu+Iu5pI98Umouk1F0m2q3dI1Yult3STinDC7mu7dUk8B3W3JBlgAH0AfV28UmLlMSRKmVfdDPB4uOCQ0D3S1/QBlaPZXM4BLOQQg4pJKizm+V8RTqnO2I+HuAX4+cUcxonXpWZT4geigTP90Ir/Fb1UfKzTTWAsL1H6kj9rbW6vE0EfgiwOLwfwTaJsi821dokWbOSki6TWm6TUX6skcUo4J3Zu4bpPB4Jm6Y4OuGqSHgmOLvgl8sHQDd/+R80Ya5SepDYVFNWSr5hL9tY2fk4Ag/k+2zhumaSt0QR/MA/dbMfQfhgg+ZfFY5UqE7FBl2zRbdhREYfNJSTiZ2l92dtYI5I9NtOATWrRxiagfl6/IlI/gYWbpFaukXHJIeKQ2bbKjPBMUwupC/wBloTBN+lBpP7HlUf7qmE0HplgA0LpPDTg74JwGOL+BEnDXVRb/IpzSWJkJ9iZ5macPQ7Oev5eJaooBp8fsIPungQiA/f/CHzUtgOKMDhZU4fTUgH5of6v6vI1gtOxP0LPuhNNp0vyRj8EvqvLXIZ4xh+1CBKdCdDK9gaOYUiAaiPiLJJcPN44RNRFH53hq0W64pNInLdJWuCXSSzZOKTwikk4j92mxYSEDtAQD7h+GjbZQ/JgMeiD1Ub3fuhkTOUDG0rIcYbzFDutXFTeM3c8NOGa7/Ac8XDwmOwT4TeVL69LapyXSS2zWIwKI/21Rfbp44AbkouzMnzOX2VB4YQMhJOiYmSeqBShowpjPyU4O2gjlug498SinakqKi8TUVE2JmkeHd/jUNqAwepM10mYzfwgmyT6qK64pSRbVFJ4uk2LJxFTPBOLib6pyUPp6kIMie5peeBJjr1MQeBZO7v4CZ4axwGeDq5Zw8BUVuzng3d1ped+FL7B91lly8HVpi7wo8vOBP0r8CLBNBH4ImsKiPybbxUOJX9hIsvPcP/AEhrdGWWJBfyp7JB6ls8YwRKoYg7po3SGwcoTl0EQR3NR5pOSUkUXSLi+6SOKRwc13wTFkdrNdYAZVWALbHLAJzwSECREk0lBw4QBOkaBStQKMzkIkOcQ6t1WLhTPUfBSIokJWVKheTee4j1Q7JSuiUlqnhL6pwzoQhHw2TFhKYbq0AKtFtecJzSSYTHVOSiLrY3yIQPkaTkVMG5QCJ4aA+weUdAG2n9BHmJUQAMy8HJQKAJXAFZ2fVxQYkyIoQdtxm6ABUwAbp3uM4Pps2bxNJBj2rCGXqZrc9v5LmI+i3S6Xa1dw13dDXDE8EAseYD9FdXeJK01NouUijdea3w1+GabRZJsbA3l98ajM3PbBu7tt+U8GbpUcWki02SKiwoxUUklZOCTaL5HCa2p5KCEImkaUcNKZJ7I6R7U7+5R+cuWhBvbO0GRMgMYfLKB3Lyi5VdtzgjC1OwEGHPVIoOpQugxicyxiVihWrZJlzYIFgixND8Q8ygHIBMMiPCbNe9rPqMD4tuhGaNVQglSkRhhwkOC4nINFLBjBAUo2RWGBKH2PujFr7QVPpUodqdVvAchgGdtTbdn419CUg+RBqVM78HoAmFMZibjNjdJxiokJnBfB3M0NUqhzjE4hsnEhWWvE+ckSBAyv2ijgsh08RtOMgeVQBWKaKKnOobZInSIkYpHgUhhSM9KQfKUx3Vh7lAKWCUTOCiCinDNckBV8CaS2dWdR4tlAGVVACl2pZwQiBoGDPy23Th4bcGg2YlRLvQPahQRs4hBoPIsT82dV1RYK75Emoj8WuD+OKSlUjzhIAWIzHoHtE4YpKcVvgkla6uk1EN0i44FC05u74Jb/R8WivJBpx6chb4mFlMwIxlZAfpickg5EAiWL/3YuBKJASk4RmiaJBQgWaJMgCHCboRBPflcFw+UZogda/hIEDYYGKSHIBMAY0PxUuj9MQlcrAGaTd4rMjkaJJakMIUzqOcgrsg4TCZZqafq5GBPEYDOUIhQS3U/LYYpKRkJBi6nKEJ+3KRoCbPn3f7JUcbL3oI+HPVe9FUzPsvqoZaqIFOUTMKiDMOBcpKyMoQiC4SxFMkRBaEGk6QKOBScSLAQ9mymYCgriLNSJMMYjGcNlTd1tngUs7BNlYplPzJsigKSyULKKJJyq8BMjAhzuYaIakzFropxkcwzEs93/VcMcBAsB2iiPMQ5iy5IyiXoIoFHi7o6EoJgBjAUTlDlkPnGAdoQmUGHqYkfBTZlmYaWV23IsidqJOwHus+2gUnMDggQgycqKXNs7WRiwYBCYJFRTS50SAAJWAMq7WtqyRBmL1IelS/mMcW/qU4ODsulH84jEQOZbMlLg9eighLimkppNYLjDwwLKeguRc0R7+dFOcCOF3mCGf6FVzGZ6gSa7Bl/TsywQDBYFIxEtGACGzJdB0lSmZ1ULAqljW0CVhgjSlHAkCMKJsreIInAb0O4l6FEFMFMRRDmS20ixI1ksiRvizVDPZkxgGSHCtARPTMxvOk8s5xSGRTbhaywwfYlG0UK4yDnyuT8BfVNlSJ6FJ9nI9Ua0YLH6Nvuo5ZIr3B/Q4hY4RQfg1YG5hUWRZKyPwRW6S/V0p3xSeCTeJv1Ti7TkqODqzdM1/o+OE4zYIwEqNV+V5S/esEsLfTYZJ81iow64jSnI6NAayXV5QgCLMsmN0MV1GwTXmXXuOHgkXsJr8RP0NGPuzIAA9A9qjAzP0mn/4VAc65dPTRwi5oqzAEyk9hG8hkrpGCZhEDCxX+D5pSIzdY16kfSnJU6iuGFEVZDBL2UyYYFMSQNal1CANMlDhu4e/qlQUEG1re5ESMYxioSznoSfOTgmIzdID/ANTzRZdxztAS8iENTJizpHsjz/NXbPaNM+UTG8PNBTCHRRD6m0+a8lj7kLAzJhqGeSMhgDCKCCT4VPupkDGf2H4KgqakR7j2EHcx3WdcbPvxYL3h3NdbjmiSBIZMCJCGKgiwcEpIBCs1/p+KiMmRInjXBxNOcUSWZD3GCBm4ZiMTNN4/OiVABIXINKKRThkg+x9009MUIkSWofx16K1WyCRgCwTo/aoiWQ4eFH+h4ByCaiK65JUqwqMcOuM2KgaaJU8O7RST8044Nkzdsklt13XlcTRZJOL5ru2rRmm7qmVkxkhjZVAjbBWqxctiEZ+hCfI2R4/6s7y3Zu2CWJovCBd/Qf0qDzZHEGOpHI8I9lGQblm4OYxDuTecgN9YrL/9dTnYEbDzPGo+UoMdycoBgwyXOMV1XXP38Q6MBwKOGf0L7ofQtMjYT+7USjtw9NAzPB2Em8AInXuGkudiRIPYAH61Uqu4YjOEYmZa/wB7xakAYmm1AMhMxYztSXUTqJCYnJFsmlxvKFRxMPdXPPepjeUweh7yT1ayK2wWsdN0EXzX+p5p/O/0vIhXzolTJDhlDTCgkVdp2fc6WRsGDFPiixdplcsxMA9IPVF0hfSpexiR7EamoIIoRo9iMZ16qertK3Edo4PIULFiUQfeJ3OWgKuJ6+yS7M61SDnXmLF2khlBGRpLkAMOL+590DueWjnhsBPlWbqOS0BtHmBXiiqUtKAD2qUt4/gQ2MdBJ6Cv8zwvKofxXCaXcfnak+daplCF+hz6s3QcJrdBRzODqp/NE0kV3ySaajgk0kcRwcXSK1ZO602a6qI4N9U07O5SZMxnpyJkdbZlRaOPbApXYXfeamQF7OTKcplcrfVDmpHFiC9lOjrVN8ZICpl4uctKhEbA8BqVJ5O6IXYYYEYEBUpUwTA+Qa6JZpYmQmGTbOCrcBBcITjC9iWm53Xu0HPBEr24Kz1cw8MlkW9oIiiKZenAACMAC0Ags1Jpgy8MyCgCRo7ysgWQuANIkMCwMkiMzDyQyQwOUyHAldUVUFhZDqhArowQzQA6kIhkQEkRGUzNMUGqVyM2ZAM5goQSGV8gthLlMRiZpDpvQZU1kTCRnWCl7K10gFFyiYII4oCnvLnREbkCyYR+6NA5nQkAkzPqnklaCGTYnKJHgQQEzMAXNtHR58+FJ1lMIM3zVziMxFLvA4jEGgw8TuFB9giWIZIEOSMis0B0GIvQCMmWU6oNUKH6bxRgSylRKvQAPQVZK0WIzZE4JuZQB7S5pc4CBnlhcuIcMCzkUMJUQhUhHK238n31EERSl5OcFgbM1HKRmCIpjGJoSCCCbhzEO3kwWzwvLKAPCkySZBTMuJAiaZnEJ+neycfggKGktCUGKEcgkadIQyIQhhQxILECsEPSL1sOOGIIEEGCAUklOIpJj28D+oG/bOqaGy3KGMREbRusjJA3OA4EZYMwRRJ4QhqdBAEGoIpcd9mqgSEphk+RsScXJnBkDkGs7FGAQYCWfKDAz5ZyUUrFTsU7tQ7yMzNQoQgmoJZHKQenMZiuq1cVRhSgNeWlBXyPwhmI4RTtqHupDzzIoumzdbVF9OBwigtu3dRRRSP/AMkWiaSK1xc0kcXJUcXuyU5LRSTdzWuJ4JHAYtq8Z4vutODhuknAcHjrhtW1a+acnpiKPnpdKBVBBiG0yobhTEPtMGJVcDKkDyEqMSHQj4tFpvTyx1WJlQpgEzT3iskE/a3jhr8I6/AHbcjPqUekAmvA6JkxTkkEpH0qO4TDGKnFuoh9UEQ1Bk7ykS9HgnxJAvF2urxUcBDUWi8WbstU3S6RxSbbs1E1q3dC0UM2ihnjHBu1FaouM1FnVH5Wl+rO6ioizuum+RbVkkeCY4O6a1TuorS8Yp1+Ddwt1ecN0ZBA7JCneNrGxuLyHzqlSUYlG288Ar9Ki88ksSPwJNJybFxTwTvglnN3PCZoUBCDhJgANq09DsIx9ApIw4ac2i4vNOTgkXd1qycGt374PB4Oqmt2caDtVib2top1yNkQEJyIxQuY6rZRwSaJYE+LK8U32u7tE8OrzZ3xCa6rdotA9h9+7Gj4BXRS4YAGTaXg/llcts8ImgD82rR4qLxwSPjjunikcOopIuLt8M8HNaoeSYmF1vT4cg4WChU5kMPDMhNI5HDU4cxrB7kX9AvVLOCcBwFKhqVmovkWbv4Bh1gy3iDrnGUjcpFHgxJwHkRqWHtfw/P+KSggCFWDX+1bpOG1TUWSou8XdglAytNhCEfFgACry7SaWL6PfeSy5fAqndITqhKdozCgAy0dX2iRIjhHxQwApFemT9pnujRLEVJbcAAQibzBVivuRAMmBAOytWmL5ERsphBko40Ww4RiBVowGYxTAMRSAkzJSMkZGSSjKoH97Ty8ST1NLRuEuxxr2YiJmtHPgT+x/wDgoitzQjgWx8mKiYDwgpBLKJkxAklZEYIKgjO2AYO2jA+YE0GN6IT1Z4bcTHCaCpbHKY6m/d45TNurzwc8YsW6ulTdpJrXDFPB1wcNkkbtbt3mzhrdQTqqPZVwBP8AmmCMRJDoPgx4gbmTPYv5TrOc8QkzkAWg40bG0kglHvx7f61gtpaH3YwF8z4s7s2FRZ1WpqYpLzk2Hae067nh6ympJCETnqplK8kwSOG5E+z2RUTTzJJT/wAQKVXQFNhhhP7oLRebM2LJqVs8MnghTpKNmgOpECWiHspik65uSkmXkwJhcGwQUEcRxndLqUdEVkP0A2MFgT5GawaSn0AyK9tnJMg4fvMwN2BQ9UF1DQ0IECV6/qvRD0QcZjrEgQLDThZc1CkIsmAjE59mXqAg/vewcHoE/wB1RFTXmuTJEkEkTM7Uc/UVYpUVKduXKtu0nmNIkYEIFwiyjEpAulHFwQAFsKBTNO7dXTcMWLh+rlasSoAOcVFkFQVCoeaio9c0EpIv1dOKcR3xSG4vtd28HVtR1WRYPgkfkHm712RJil3yGExmoVOEUwZB6Kfb2pgzJUjlVdvBFNJjhq7uzhaK8wP+063FfIn6H+peRou7r4s6vFtNJ4Y6IOBlA62dTqofKxnzQi990nY8VMZIinWINuBp5RWbrAwJQ7g5ns/rVgAkJhg4OxmDVOQmCNnaTokUvSLmIgwuk/STDQDwYIJBQWFAp80STLn5cBxA7sNpPghkoGH26qOHdUgwKMZzTY/H/CES8C90IIm3MKCiH34oG9wFHpmQy9M7qC1TA+siVkvhwtSUm/u5KGMtwRg6pUZUsGaEoy2VXqAT8YQhJCMPSzFBljyFgSUcAEiWU0i8SUsMzEOEEsrbpwdXDhugm5cJotNFgmj8ZJppEckxycX1ZOG6SK6t3Qku5pxZJL6cN8dm5XSifA02zbEyC5BiW28u4Cmzrhum+3FpRoaoD6kKdPXaN/AeAwH5Dh1aKpqs0guAh+1PzOxAyRP9Hgx5ng04PJapSq7VoMQGAuBKwfav3dMUW6pMt3g1bSw6x4c0ISE6mBx6s6uEcCjFLwDi5oLPD+vxPBuyeOLqos2SS48XdnDcXTPMZvOKB2KTidFXqR+uQ2KcNuq05nd9ODh4pp1TVhhIvkc+R4M1pwdPHvntfamnXBtcChDoAytTKOSwe4fWIxnbpWKgfactdp3WV7fwhxCeMTWuWq6qKiofwJURU3mk8V1wdcRx08NLuT8Q8Im/dndTaeBvvgmbuTm3WlTdyfhd8d3TdNvNopwEyHtg38UlxkLp2PAT4+S0hJDBxsDQWCY7zikNNm+n+8Lu+IS1364GWtcA4NgmvlUHKCmiRyTikcUj44RioqLaocN1PNwMPyWEfKfTWyNzkeHo5MOaJYj5T/ynjnDx7iySwHnPi2y+nBqOG3AcHXB3d3d56cExd5Jl4bWizu+nI74CJSBkRiKZlFmLR7a/YJ7skEQCVXQFHMlSHpCPBz6jdd3DFNRcIrzcJ490H4O+CTSRxSM8Epw3FGeyoxX7i8YR58TGYcrrYQuP4VCDU2RKggA7iumM7swZGJ3Fk4tRfaj7EToQ6fA3+8VqfMIIwf8ACsbzxosH9b9q0WcN3g21wNFOvwO7u7urRZ3Y3TkbNbs8NngM11ccNq82dXdX24O6Eb5sAhDslR5D1QFcND5x6D2OTW6AIxCy/wBZ959uqwrP6s193DJwKE8DdRfdBNGOccerpabuOAozwz40nFJ2CdeoqKhrITgD8EV7weZ6s6vqyZ4aVsVKqNckIweTEvj2p1cTbVOG0cXdJi7W7zZw8yLQLunBKYK7oA/vElNaaSeGuDvhtUVu6Lv5BW19NkJJATmOk7PVepKrgg1ot1pcWAJogyewmc0/wUSk1UdY0bf/2Q=="
st.markdown(
    '<img src="data:image/jpeg;base64,' + _BANNER_B64 + '"'
    ' style="width:100%;border-radius:8px;margin-bottom:16px;display:block">',
    unsafe_allow_html=True
)


MONTH_LABELS = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}

MANUAL_URL_MAPPING = {
    21271: "https://www.voyage-prive.com/login/index",
}

def rewrite_url(carambola_url):
    if pd.isna(carambola_url):
        return None
    prefix = "http://fr-carambola.bovpg.net//campaign/microsite/"
    slug = str(carambola_url).replace(prefix, "")
    if slug == "index":
        return f"https://www.voyage-prive.com/login/{slug}"
    return f"https://www.voyage-prive.com/offres/{slug}"

def url_label(url):
    """Retire le domaine — garde uniquement le chemin."""
    if pd.isna(url):
        return None
    return str(url).replace("https://www.voyage-prive.com/", "")

def parse_float(val):
    if pd.isna(val):
        return None
    try:
        return float(str(val).replace(",", "."))
    except ValueError:
        return None

def slug_from_url(url):
    if pd.isna(url):
        return None
    return str(url).replace("https://www.voyage-prive.com/offres/", "")\
                   .replace("https://www.voyage-prive.com/login/", "login/")

@st.cache_data
def load_data(tableau_file, carambola_file):
    df_cara = pd.read_excel(carambola_file)
    df_cara = df_cara[df_cara["Campaign id"] != 0].copy()
    df_cara["vp_url"] = df_cara["Campaign URL"].apply(rewrite_url)
    df_cara = df_cara[["Campaign id", "Campaign name", "vp_url"]].rename(
        columns={"Campaign id": "campaign_id", "Campaign name": "campaign_name"}
    )

    df_tab = pd.read_csv(tableau_file, sep=";")
    df_tab = df_tab.rename(columns={
        "Campaign Id (h1)": "campaign_id",
        "Measure Names": "metric",
        "Measure Values": "value",
        "Date granularity": "month",
        "Registration Year": "year"
    })
    df_tab = df_tab[df_tab["metric"].isin(["TTV", "Bookings"])].copy()
    df_tab = df_tab[df_tab["campaign_id"].notna()].copy()
    df_tab["campaign_id"] = df_tab["campaign_id"].astype(int)
    df_tab["value"] = df_tab["value"].apply(parse_float)
    df_tab = df_tab[(df_tab["year"] == 2025) & (df_tab["month"].between(1, 12))].copy()
    df_tab["month_label"] = df_tab["month"].map(MONTH_LABELS)

    df = df_tab.merge(df_cara, on="campaign_id", how="left")

    # Appliquer le mapping manuel pour les IDs orphelins
    for cid, url in MANUAL_URL_MAPPING.items():
        mask = (df["campaign_id"] == cid) & df["vp_url"].isna()
        df.loc[mask, "vp_url"] = url

    df["slug"] = df["vp_url"].apply(slug_from_url)
    df["url_label"] = df["vp_url"].apply(url_label)
    # Fallback : ID si aucune URL trouvée
    df["url_label"] = df["url_label"].fillna("ID:" + df["campaign_id"].astype(str))
    return df

# ── UI ──
st.title("✈️ Voyage Privé · Dashboard SEO Performance")
st.markdown("Top pages par mois · TTV & Bookings")

with st.sidebar:
    st.header("📂 Fichiers de données")
    tableau_file = st.file_uploader("Export Tableau (CSV)", type=["csv"])
    carambola_file = st.file_uploader("Export Carambola (XLSX)", type=["xlsx"])
    st.divider()
    st.caption("Les fichiers ne sont pas stockés — traitement local.")

if not tableau_file or not carambola_file:
    st.info("👈 Charge les deux fichiers dans la sidebar pour commencer.")
    st.stop()

df = load_data(tableau_file, carambola_file)

with st.sidebar:
    st.header("🔧 Filtres")
    months_available = sorted(df["month"].unique())
    selected_months = st.multiselect(
        "Mois", options=months_available, default=months_available,
        format_func=lambda x: MONTH_LABELS[x]
    )
    top_n = st.slider("Top N pages", min_value=5, max_value=150, value=10)

df_filtered = df[df["month"].isin(selected_months)].copy()
ordered_month_labels = [MONTH_LABELS[m] for m in sorted(selected_months)]

# ── KPIs globaux ──
col1, col2 = st.columns(2)
total_ttv = df_filtered[df_filtered["metric"] == "TTV"]["value"].sum()
total_bkg = df_filtered[df_filtered["metric"] == "Bookings"]["value"].sum()
col1.metric("💶 TTV Total (période)", f"{total_ttv:,.0f} €")
col2.metric("🛎️ Bookings Total (période)", f"{int(total_bkg):,}")
st.divider()

# ──────────────────────────────────────────
# PRÉPARATION DES DONNÉES AGRÉGÉES
# ──────────────────────────────────────────

def get_agg(df_in):
    return (
        df_in.groupby(
            ["month", "month_label", "campaign_id", "campaign_name", "vp_url", "url_label", "slug"],
            dropna=False
        )["value"].sum().reset_index()
    )

df_ttv_agg  = get_agg(df_filtered[df_filtered["metric"] == "TTV"])
df_bkg_agg  = get_agg(df_filtered[df_filtered["metric"] == "Bookings"])

# Top N par TTV (référence commune pour les graphiques merged)
df_ttv_global = (
    df_ttv_agg.groupby(["campaign_id", "campaign_name", "vp_url", "url_label"])["value"]
    .sum().reset_index().rename(columns={"value": "TTV"})
    .sort_values("TTV", ascending=False).head(top_n)
)
df_bkg_global = (
    df_bkg_agg.groupby(["campaign_id", "campaign_name", "vp_url", "url_label"])["value"]
    .sum().reset_index().rename(columns={"value": "Bookings"})
)

# Fusion sur les top IDs TTV
top_ids = df_ttv_global["campaign_id"].tolist()
df_merged_global = df_ttv_global.merge(df_bkg_global, on=["campaign_id", "campaign_name", "vp_url", "url_label"], how="left")
df_merged_global["Bookings"] = df_merged_global["Bookings"].fillna(0)
df_merged_global = df_merged_global.sort_values("TTV", ascending=True)  # pour bar horizontal

# ──────────────────────────────────────────
# GRAPHIQUES MERGED TTV + BOOKINGS
# ──────────────────────────────────────────

st.subheader(f"📊 Top {top_n} URLs · TTV & Bookings (période sélectionnée)")

# Palette commune
palette = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Light24
df_donut = df_merged_global.sort_values("TTV", ascending=False).reset_index(drop=True)
df_donut["color"] = [palette[i % len(palette)] for i in range(len(df_donut))]

col_donut, col_bkg_table = st.columns([1, 1])

with col_donut:
    fig_donut = go.Figure(go.Pie(
        labels=df_donut["url_label"],
        values=df_donut["TTV"],
        hole=0.45,
        marker=dict(colors=df_donut["color"]),
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>TTV : %{value:,.0f} €<br>Part : %{percent}<extra></extra>",
        sort=False
    ))
    fig_donut.update_layout(
        title=f"TTV · Top {top_n} URLs",
        height=600,
        showlegend=False,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_bkg_table:
    st.markdown(f"**Bookings · Top {top_n} URLs**")
    df_bkg_display = df_donut[["url_label", "Bookings", "TTV", "color"]].copy()
    df_bkg_display = df_bkg_display.sort_values("Bookings", ascending=False).reset_index(drop=True)

    rows_html = ""
    for _, row in df_bkg_display.iterrows():
        dot = f'<span style="display:inline-block;width:11px;height:11px;border-radius:50%;background:{row["color"]};margin-right:6px;vertical-align:middle"></span>'
        rows_html += f"<tr><td>{dot}{row['url_label']}</td><td style='text-align:right'><b>{int(row['Bookings']):,}</b></td><td style='text-align:right;color:#888'>{row['TTV']:,.0f} €</td></tr>"

    table_html = f"""
    <style>
    .bkg-table {{width:100%;border-collapse:collapse;font-size:12.5px}}
    .bkg-table th {{text-align:left;padding:6px 8px;border-bottom:2px solid #ddd;color:#555;font-size:12px}}
    .bkg-table td {{padding:4px 8px;border-bottom:1px solid #f0f0f0}}
    .bkg-table tr:hover td {{background:#f7f7f7}}
    </style>
    <div style="max-height:560px;overflow-y:auto">
    <table class="bkg-table">
      <thead><tr><th>URL</th><th style="text-align:right">Bookings</th><th style="text-align:right">TTV (€)</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table></div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

# ── Bar columns évolution mensuelle ──
st.subheader(f"📈 Évolution mensuelle · Top {top_n} URLs · TTV & Bookings")

col_ev1, col_ev2 = st.columns(2)

for ev_col, df_trend_src, metric_label, color_scale in [
    (col_ev1, df_ttv_agg, "TTV (€)", "Blues"),
    (col_ev2, df_bkg_agg, "Bookings", "Oranges"),
]:
    with ev_col:
        df_t = df_trend_src[df_trend_src["campaign_id"].isin(top_ids)].copy()
        df_t["url_label"] = df_t["url_label"].fillna("ID:" + df_t["campaign_id"].astype(str))
        df_t = df_t.sort_values("month")
        fig_ev = px.bar(
            df_t,
            x="month_label",
            y="value",
            color="url_label",
            barmode="group",
            title=metric_label,
            labels={"value": metric_label, "month_label": "Mois", "url_label": "URL"},
            category_orders={"month_label": ordered_month_labels},
            height=950,
        )
        fig_ev.update_layout(
            legend=dict(orientation="h", yanchor="top", y=-0.18, font=dict(size=9)),
            margin=dict(b=200),
            xaxis_tickangle=-30,
        )
        st.plotly_chart(fig_ev, use_container_width=True)


# ── Vue par mois ──
st.divider()
st.subheader("📅 Vue détaillée par mois")

selected_month_detail = st.selectbox(
    "Choisir un mois", options=sorted(selected_months),
    format_func=lambda x: MONTH_LABELS[x]
)

df_month = df_filtered[df_filtered["month"] == selected_month_detail]

df_month_ttv = (
    df_month[df_month["metric"] == "TTV"]
    .groupby(["campaign_id", "campaign_name", "vp_url", "url_label"])["value"]
    .sum().reset_index().rename(columns={"value": "TTV"})
    .sort_values("TTV", ascending=False).head(top_n)
)
df_month_bkg = (
    df_month[df_month["metric"] == "Bookings"]
    .groupby(["campaign_id", "vp_url", "url_label"])["value"]
    .sum().reset_index().rename(columns={"value": "Bookings"})
)
df_month_merged = df_month_ttv.merge(df_month_bkg, on=["campaign_id", "vp_url", "url_label"], how="left")
df_month_merged["Bookings"] = df_month_merged["Bookings"].fillna(0)
df_month_merged = df_month_merged.sort_values("TTV", ascending=True)

fig_month = go.Figure()
fig_month.add_trace(go.Bar(
    y=df_month_merged["url_label"], x=df_month_merged["TTV"],
    name="TTV (€)", orientation="h", marker_color="#1d6fa4", opacity=0.85
))
fig_month.add_trace(go.Bar(
    y=df_month_merged["url_label"], x=df_month_merged["Bookings"],
    name="Bookings", orientation="h", marker_color="#f4a840", opacity=0.85
))
fig_month.update_layout(
    barmode="group",
    height=max(400, top_n * 45),
    title=f"Top {top_n} URLs · {MONTH_LABELS[selected_month_detail]}",
    yaxis=dict(tickfont=dict(size=10)),
    xaxis=dict(title="Valeur"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    margin=dict(l=20, r=40, t=60, b=20)
)
st.plotly_chart(fig_month, use_container_width=True)

st.dataframe(
    df_month_merged[["campaign_id", "campaign_name", "vp_url", "TTV", "Bookings"]]
    .rename(columns={"campaign_id": "ID", "campaign_name": "Campagne", "vp_url": "URL VP"}),
    hide_index=True, use_container_width=True
)

# ── Tableau récap fusionné ──
st.divider()
st.subheader("📊 Tableau récap · TTV + Bookings (toute la période sélectionnée)")

df_recap = df_merged_global.sort_values("TTV", ascending=False).copy()
df_recap["TTV / Booking (€)"] = (df_recap["TTV"] / df_recap["Bookings"].replace(0, float("nan"))).round(0)

df_recap_display = df_recap.head(top_n).copy()
df_recap_display["TTV (€)"]        = df_recap_display["TTV"].map(lambda x: f"{x:,.0f}")
df_recap_display["Bookings"]       = df_recap_display["Bookings"].map(lambda x: f"{int(x):,}")
df_recap_display["TTV / Booking (€)"] = df_recap_display["TTV / Booking (€)"].map(
    lambda x: f"{x:,.0f}" if pd.notna(x) else "-"
)
df_recap_display = df_recap_display.rename(columns={
    "campaign_id": "ID", "campaign_name": "Nom campagne", "vp_url": "URL VP"
})[["ID", "Nom campagne", "URL VP", "TTV (€)", "Bookings", "TTV / Booking (€)"]]

st.caption(f"Top {top_n} pages triées par TTV décroissant")
st.dataframe(df_recap_display, use_container_width=True, hide_index=True)

csv = df_recap[["campaign_id", "campaign_name", "vp_url", "TTV", "Bookings", "TTV / Booking (€)"]].to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Exporter le récap complet (CSV)",
    data=csv, file_name="vp_seo_recap.csv", mime="text/csv"
)
