from flask import Flask, render_template, request
from DtaSchedule import getSchedule
from createRandom import genMatrices
from helperFns import arrangeDF, arrangeDFseq
import time

app = Flask(__name__)

df = {}

@app.route('/')
def root():
    	return render_template('home.html')

@app.route('/random')
def randomInput():
	return render_template('random.html')

@app.route('/randomOutput', methods=['POST'])
def randomOutput():
	N = int(request.form.get('N'))
	T = int(request.form.get('T'))
	cij,d_it,h_it = genMatrices(N+1, T)
	Visiting_Time,Delivery_Quantity,PathEachTime = getSchedule(N+1,T,cij,d_it,h_it)
	df_qty = arrangeDF(N+1,T,Visiting_Time,Delivery_Quantity)
	df_seq = arrangeDFseq(N+1,T,PathEachTime)
	if (N<=10 and T<=10):
		results_page = 'results.html'
	else:
		results_page = 'results_more.html'
		df['df_qty'] = df_qty
		df['df_seq'] = df_seq
	return render_template(results_page, table_qty = df_qty.to_html(classes='qty',max_rows=10,max_cols=10), table_seq = df_seq.to_html(classes='qty',max_rows=10,max_cols=10))

@app.route('/manual')
def manualInput():
	return render_template('manual.html')

@app.route('/manualOutput', methods=['POST'])
def manualOutput():
	N = int(request.form.get('N'))
	T = int(request.form.get('T'))
	C = request.form.get('C')
	D = request.form.get('D')
	H = request.form.get('H')
	C_list = C.split()
	D_list = D.split()
	H_list = H.split()
	if len(C_list)!=((N+1)*(N+1)) or len(D_list)!=(N*T) or len(H_list)!=(N*T):
		return "Dimension of matrix is incorrect."
	else:
		C_list = [float(C_list[i]) for i in range(len(C_list))]
		cij = zip(*[iter(C_list)]*(N+1))
		D_list = [float(D_list[i]) for i in range(len(D_list))]
		d_it = [[0]*T] +  zip(*[iter(D_list)]*T)
		H_list = [float(H_list[i]) for i in range(len(H_list))]
		h_it = [[0]*T] + zip(*[iter(H_list)]*T)
	Visiting_Time,Delivery_Quantity,PathEachTime = getSchedule(N+1,T,cij,d_it,h_it)
	df_qty = arrangeDF(N+1,T,Visiting_Time,Delivery_Quantity)
	df_seq = arrangeDFseq(N+1,T,PathEachTime)
	if (N<=10 and T<=10):
		results_page = 'results.html'
	else:
		results_page = 'results_more.html'
	return render_template(results_page, table_qty = df_qty.to_html(classes='qty',max_rows=10,max_cols=10), table_seq = df_seq.to_html(classes='qty',max_rows=10,max_cols=10))


@app.route('/text')
def textInput():
	return render_template('text.html')

allowed_ext = set(['txt'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1] in allowed_ext

@app.route('/textOutput', methods=['POST'])
def textOutput():
	if request.method == 'POST':
		f = request.files['file']
		if f and allowed_file(f.filename):
			fval = f.getvalue()
			f_list = fval.split()
			f_list = [float(f_list[i]) for i in range(len(f_list))]
			N = int(f_list[0])
			T = int(f_list[1])
			l = 2 + (N+1)*(N+1) + (N*T) + (N*T)
			if len(f_list) == l:
				cij = zip(*[iter(f_list[2:int(2+(N+1)*(N+1))])]*(N+1))
				d_it = [[0]*T] +  zip(*[iter(f_list[int(2+(N+1)*(N+1)):int(2+(N+1)*(N+1)+(N*T))])]*T)
				h_it = h_it = [[0]*T] + zip(*[iter(f_list[int(2+(N+1)*(N+1)+(N*T)):int(2+(N+1)*(N+1)+2*(N*T))])]*T)
				Visiting_Time,Delivery_Quantity,PathEachTime = getSchedule(N+1,T,cij,d_it,h_it)
				df_qty = arrangeDF(N+1,T,Visiting_Time,Delivery_Quantity)
				df_seq = arrangeDFseq(N+1,T,PathEachTime)
				if (N<=10 and T<=10):
					results_page = 'results.html'
				else:
					results_page = 'results_more.html'
				return render_template(results_page, table_qty = df_qty.to_html(classes='qty',max_rows=10,max_cols=10), table_seq = df_seq.to_html(classes='qty',max_rows=10,max_cols=10))
			else:
				return 'Invalid data.'
		else:
			return 'Invalid file.'

@app.route('/results_all')
def results_all():
	df_qty = df['df_qty']
	df_seq = df['df_seq']
	return render_template('results_all.html', table_qty = df_qty.to_html(classes='qty'), table_seq = df_seq.to_html(classes='qty'))


if  __name__ == '__main__':
    	app.run(debug=True)
